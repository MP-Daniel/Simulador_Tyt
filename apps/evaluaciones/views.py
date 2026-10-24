import random
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from cuestionarios.models import Cuestionario
from banco_preguntas.models import Pregunta, OpcionRespuesta
from .models import Intento, RespuestaIntento
from .serializers import (
    PreguntaExamenSeguraSerializer,
    IntentoListSerializer,
    RevisionIntentoSerializer
)
from authentication.permissions import require_permission


class IniciarIntentoView(APIView):
    """
    Inicia un nuevo intento de examen de forma segura (Sec 2.5 y Reglas R04, R08).
    - Valida que SOLO los usuarios con rol 'Estudiante' y permiso 'cuestionarios.rendir'
      puedan presentar exámenes oficiales, protegiendo las métricas académicas.
    - Bloquea a Administradores y Docentes con HTTP 403 Forbidden.
    - Valida disponibilidad en el servidor (fecha apertura/cierre y estado activo).
    - Valida que el estudiante no haya superado el número de intentos permitidos.
    - Oculta las respuestas correctas al frontend durante la presentación del examen.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # BLINDAJE DE NEGOCIO: Solo estudiantes matriculados pueden rendir exámenes oficiales
        rol_nombre = user.rol.nombre if user.rol else None
        tiene_permiso_rendir = user.tiene_permiso('cuestionarios.rendir')

        if rol_nombre != 'Estudiante' or not tiene_permiso_rendir:
            return Response({
                "error": "Acceso denegado: Solo los usuarios con rol 'Estudiante' pueden presentar evaluaciones oficiales. Si es docente o administrador, utilice la opción de Previsualización."
            }, status=status.HTTP_403_FORBIDDEN)

        cuestionario_id = request.data.get('cuestionario_id')
        if not cuestionario_id:
            return Response({'detail': 'El campo "cuestionario_id" es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        cuestionario = get_object_or_404(Cuestionario, id=cuestionario_id)

        # 1. Validación en el servidor de disponibilidad e intentos (R08, R04)
        puede_iniciar, motivo = cuestionario.puede_iniciar_estudiante(user)
        if not puede_iniciar:
            return Response({
                'detail': f'No es posible iniciar el cuestionario: {motivo}',
                'codigo': 'DISPONIBILIDAD_BLOQUEADA'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Verificar si ya hay un intento en progreso para retomarlo
        intento_existente = Intento.objects.filter(
            cuestionario=cuestionario,
            estudiante=user,
            estado_intento='en_progreso'
        ).first()

        if intento_existente:
            intento = intento_existente
        else:
            intentos_previos = Intento.objects.filter(cuestionario=cuestionario, estudiante=user).count()
            intento = Intento.objects.create(
                cuestionario=cuestionario,
                estudiante=user,
                numero_intento=intentos_previos + 1,
                estado_intento='en_progreso',
                puntaje_total_posible=cuestionario.puntaje_total_posible,
                total_preguntas=cuestionario.cuestionario_preguntas.count()
            )

        # 3. Construir lista de preguntas segura (SIN 'es_correcta' y SIN 'retroalimentacion')
        cps = list(cuestionario.cuestionario_preguntas.select_related('pregunta__categoria').prefetch_related('pregunta__opciones'))

        if cuestionario.mezclar_preguntas:
            # Semilla reproducible basada en el ID del intento para estabilidad ante recargas
            r = random.Random(intento.id)
            r.shuffle(cps)

        preguntas_payload = []
        for idx, cp in enumerate(cps, 1):
            p = cp.pregunta
            opciones = list(p.opciones.all())
            if cuestionario.mezclar_respuestas:
                r_opt = random.Random(intento.id + p.id)
                r_opt.shuffle(opciones)

            preguntas_payload.append({
                'id': p.id,
                'categoria_nombre': p.categoria.nombre,
                'tipo': p.tipo,
                'texto_base': p.texto_base,
                'enunciado': p.enunciado,
                'puntaje': cp.puntaje,
                'orden': idx,
                'opciones': opciones
            })

        serializer = PreguntaExamenSeguraSerializer(preguntas_payload, many=True)

        return Response({
            'intento_id': intento.id,
            'numero_intento': intento.numero_intento,
            'cuestionario': {
                'id': cuestionario.id,
                'nombre': cuestionario.nombre,
                'descripcion': cuestionario.descripcion,
                'tiempo_limite_minutos': cuestionario.tiempo_limite_minutos,
                'calificacion_maxima': str(cuestionario.calificacion_maxima),
                'total_preguntas': len(preguntas_payload)
            },
            'preguntas': serializer.data
        }, status=status.HTTP_200_OK)


class FinalizarIntentoView(APIView):
    """
    Finaliza el intento, ejecuta el cálculo automático de la nota en Django
    y registra las respuestas contestadas y omitidas (Sec 2.5 y Reglas R09, R10).
    Fórmula: Calificación = (puntaje_obtenido / puntaje_total_posible) * calificacion_maxima
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, intento_id):
        intento = get_object_or_404(Intento, id=intento_id)

        # SEGURIDAD CRÍTICA (Sec 2.5): Solo el propietario puede finalizar su propio intento
        if intento.estudiante != request.user:
            raise PermissionDenied("No tienes autorización para modificar los intentos de otro estudiante.")

        if intento.estado_intento == 'finalizado':
            return Response({
                'detail': 'Este intento ya fue finalizado y calificado previamente.',
                'intento_id': intento.id,
                'calificacion': str(intento.calificacion),
                'resultado': intento.resultado
            }, status=status.HTTP_200_OK)

        respuestas_enviadas = request.data.get('respuestas', {})  # { str(pregunta_id): opcion_id o letra }
        marcas_revision = request.data.get('banderas', {})         # { str(pregunta_id): bool }
        duracion_segundos = int(request.data.get('duracion_segundos', 0))

        cuestionario = intento.cuestionario
        cps = cuestionario.cuestionario_preguntas.select_related('pregunta').prefetch_related('pregunta__opciones')

        puntaje_total_posible = Decimal('0.00')
        puntaje_obtenido = Decimal('0.00')
        aciertos = 0
        errores = 0
        omitidas = 0

        with transaction.atomic():
            for cp in cps:
                pregunta = cp.pregunta
                peso = cp.puntaje
                puntaje_total_posible += peso

                p_id_str = str(pregunta.id)
                opcion_id_o_letra = respuestas_enviadas.get(p_id_str, None)
                marcada = bool(marcas_revision.get(p_id_str, False))

                opcion_obj = None
                if opcion_id_o_letra is not None and str(opcion_id_o_letra).strip() != '':
                    # Buscar por ID numérico o por letra
                    if str(opcion_id_o_letra).isdigit():
                        opcion_obj = pregunta.opciones.filter(id=int(opcion_id_o_letra)).first()
                    else:
                        opcion_obj = pregunta.opciones.filter(letra__iexact=str(opcion_id_o_letra).strip()).first()

                if opcion_obj:
                    # Pregunta Respondida
                    es_correcta = opcion_obj.es_correcta
                    if es_correcta:
                        aciertos += 1
                        pts_ganados = peso
                        puntaje_obtenido += peso
                    else:
                        errores += 1
                        pts_ganados = Decimal('0.00')

                    RespuestaIntento.objects.update_or_create(
                        intento=intento,
                        pregunta=pregunta,
                        defaults={
                            'opcion_seleccionada': opcion_obj,
                            'es_acierto': es_correcta,
                            'puntaje_obtenido': pts_ganados,
                            'marcada_revision': marcada
                        }
                    )
                else:
                    # Regla R09: Pregunta Omitida / En blanco (conserva registro con 0.00 pts)
                    omitidas += 1
                    RespuestaIntento.objects.update_or_create(
                        intento=intento,
                        pregunta=pregunta,
                        defaults={
                            'opcion_seleccionada': None,
                            'es_acierto': False,
                            'puntaje_obtenido': Decimal('0.00'),
                            'marcada_revision': marcada
                        }
                    )

            # Cálculo estricto de la calificación según especificación Saber TyT:
            # Calificación = (puntaje_obtenido / puntaje_total_posible) * calificacion_maxima
            max_grade = cuestionario.calificacion_maxima
            if puntaje_total_posible > Decimal('0.00'):
                calc_raw = (puntaje_obtenido / puntaje_total_posible) * max_grade
                calificacion_final = round(calc_raw, 2)
            else:
                calificacion_final = Decimal('0.00')

            aprobado = (calificacion_final >= cuestionario.calificacion_aprobacion)
            resultado_str = 'aprobado' if aprobado else 'reprobado'

            # Actualización del Intento
            intento.fecha_fin = timezone.now()
            intento.duracion_segundos = duracion_segundos
            intento.puntaje_obtenido = puntaje_obtenido
            intento.puntaje_total_posible = puntaje_total_posible
            intento.calificacion = calificacion_final
            intento.estado_intento = 'finalizado'
            intento.resultado = resultado_str
            intento.total_preguntas = cps.count()
            intento.aciertos = aciertos
            intento.errores = errores
            intento.omitidas = omitidas
            intento.save()

        return Response({
            'intento_id': intento.id,
            'calificacion': str(calificacion_final),
            'calificacion_maxima': str(cuestionario.calificacion_maxima),
            'resultado': resultado_str,
            'aprobado': aprobado,
            'puntaje_obtenido': str(puntaje_obtenido),
            'puntaje_total_posible': str(puntaje_total_posible),
            'total_preguntas': intento.total_preguntas,
            'aciertos': aciertos,
            'errores': errores,
            'omitidas': omitidas,
            'permitir_revision': cuestionario.permitir_revision,
            'detail': f'Examen finalizado con éxito. Calificación: {calificacion_final} / {cuestionario.calificacion_maxima}'
        }, status=status.HTTP_200_OK)


class RevisionIntentoView(APIView):
    """
    Consulta de resultados y revisión pedagógica del intento (Sec 2.5).
    SEGURIDAD CRÍTICA:
    - Evita que un estudiante consulte o modifique intentos y calificaciones de otro.
    - Solo el propio estudiante o un usuario con permiso 'resultados.consultar_todos' puede ver la revisión.
    - Si el cuestionario tiene permitir_revision=False, oculta las respuestas correctas.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, intento_id):
        intento = get_object_or_404(
            Intento.objects.select_related('cuestionario', 'estudiante')
            .prefetch_related('respuestas__pregunta__categoria', 'respuestas__opcion_seleccionada', 'respuestas__pregunta__opciones'),
            id=intento_id
        )

        user = request.user
        # Verificación estricta de seguridad
        puede_ver_todos = user.tiene_permiso('resultados.consultar_todos')
        if intento.estudiante != user and not puede_ver_todos:
            raise PermissionDenied("Acceso denegado: No tienes autorización para consultar las calificaciones de otro estudiante.")

        serializer = RevisionIntentoSerializer(intento)
        data = serializer.data

        # Si el cuestionario tiene prohibida la revisión, ocultar las respuestas correctas y feedback
        if not intento.cuestionario.permitir_revision and not puede_ver_todos:
            for resp in data.get('respuestas', []):
                resp['opcion_correcta_letra'] = None
                resp['opcion_correcta_texto'] = None
                resp['retroalimentacion'] = "La revisión de respuestas no está habilitada para este cuestionario."
                resp['todas_las_opciones'] = []

        return Response(data)


class MisIntentosView(APIView):
    """Retorna el historial de intentos exclusivos del estudiante autenticado (Sec 2.5)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        intentos = Intento.objects.filter(estudiante=request.user).select_related('cuestionario').order_by('-fecha_inicio')
        serializer = IntentoListSerializer(intentos, many=True)
        return Response(serializer.data)


class TodosLosIntentosView(APIView):
    """Consulta global de resultados para Docentes y Administradores (Sec 2.2)."""
    permission_classes = [IsAuthenticated, require_permission('resultados.consultar_todos')]

    def get(self, request):
        cuestionario_id = request.query_params.get('cuestionario')
        qs = Intento.objects.select_related('cuestionario', 'estudiante').order_by('-fecha_inicio')

        if cuestionario_id:
            qs = qs.filter(cuestionario_id=cuestionario_id)

        serializer = IntentoListSerializer(qs, many=True)
        return Response(serializer.data)
