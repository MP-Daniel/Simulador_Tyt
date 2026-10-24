from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Cuestionario, CuestionarioPregunta
from .serializers import CuestionarioSerializer, CuestionarioEstudianteSerializer
from authentication.permissions import require_permission


class CuestionarioViewSet(viewsets.ModelViewSet):
    """
    Gestión y configuración de cuestionarios (Sec 2.4).
    Aplica autorización en servidor y control de disponibilidad estricto (R01, R04, R08).
    """
    queryset = Cuestionario.objects.all().prefetch_related('cuestionario_preguntas__pregunta').order_by('-id')
    serializer_class = CuestionarioSerializer

    def get_permissions(self):
        # La consulta de cuestionarios habilitados para estudiantes requiere autenticación básica
        if self.action in ['disponibles', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), require_permission('cuestionarios.gestionar')()]

    def get_serializer_class(self):
        user = self.request.user
        if self.action == 'disponibles' or (user.is_authenticated and user.es_estudiante and not user.es_administrador):
            return CuestionarioEstudianteSerializer
        return CuestionarioSerializer

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        cuestionario = self.get_object()
        cuestionario.activo = not cuestionario.activo
        cuestionario.save()
        return Response({
            'detail': f"Cuestionario {'activado' if cuestionario.activo else 'desactivado'} correctamente.",
            'activo': cuestionario.activo
        })

    @action(detail=False, methods=['get'], url_path='disponibles')
    def disponibles(self, request):
        """
        Endpoint para estudiantes (Sec 2.5):
        "Con el rol estudiante, mostrar solamente los cuestionarios disponibles."
        Filtra cuestionarios activos, en estado 'disponible' y dentro del rango de apertura y cierre (R08).
        """
        ahora = timezone.now()
        qs = Cuestionario.objects.filter(
            activo=True,
            estado='disponible',
            fecha_apertura__lte=ahora,
            fecha_cierre__gte=ahora
        ).prefetch_related('cuestionario_preguntas')

        serializer = CuestionarioEstudianteSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='previsualizar')
    def previsualizar(self, request, pk=None):
        """
        Modo Previsualización (Sandbox) para Docentes y Administradores.
        - Muestra las preguntas, opciones (indicando la correcta) y retroalimentación pedagógica.
        - NO genera ningún intento en la base de datos ni altera métricas de estudiantes.
        - Bloquea el acceso a estudiantes estándar con HTTP 403 Forbidden.
        """
        user = request.user
        es_autorizado = (
            user.is_superuser or
            user.es_administrador or
            user.tiene_permiso('cuestionarios.gestionar') or
            (user.rol and user.rol.nombre in ['Docente', 'Docente Evaluador', 'Administrador'])
        )

        if not es_autorizado:
            return Response({
                "error": "Acceso denegado: La previsualización de cuestionarios está reservada exclusivamente para docentes y administradores."
            }, status=status.HTTP_403_FORBIDDEN)

        cuestionario = self.get_object()
        cps = cuestionario.cuestionario_preguntas.select_related('pregunta__categoria').prefetch_related('pregunta__opciones').order_by('orden', 'id')

        preguntas_data = []
        for idx, cp in enumerate(cps, 1):
            p = cp.pregunta
            opciones = []
            for opt in p.opciones.all():
                opciones.append({
                    'id': opt.id,
                    'letra': opt.letra,
                    'texto': opt.texto,
                    'es_correcta': opt.es_correcta
                })

            preguntas_data.append({
                'id': p.id,
                'orden': cp.orden or idx,
                'categoria': p.categoria.nombre if p.categoria else 'General',
                'tipo': p.tipo,
                'tipo_display': p.get_tipo_display(),
                'texto_base': p.texto_base,
                'enunciado': p.enunciado,
                'puntaje': str(cp.puntaje),
                'retroalimentacion': p.retroalimentacion or 'Sin retroalimentación registrada.',
                'opciones': opciones
            })

        return Response({
            'cuestionario': {
                'id': cuestionario.id,
                'nombre': cuestionario.nombre,
                'descripcion': cuestionario.descripcion,
                'tiempo_limite_minutos': cuestionario.tiempo_limite_minutos,
                'intentos_permitidos': cuestionario.intentos_permitidos,
                'calificacion_maxima': str(cuestionario.calificacion_maxima),
                'calificacion_aprobacion': str(cuestionario.calificacion_aprobacion),
                'mezclar_preguntas': cuestionario.mezclar_preguntas,
                'mezclar_respuestas': cuestionario.mezclar_respuestas,
                'permitir_revision': cuestionario.permitir_revision,
                'estado': cuestionario.estado,
                'total_preguntas': len(preguntas_data),
                'puntaje_total_posible': str(cuestionario.puntaje_total_posible),
            },
            'es_sandbox': True,
            'modo': 'previsualizacion_docente',
            'mensaje': 'Modo Previsualización Activo: No se registrarán intentos ni notas en la base de datos.',
            'preguntas': preguntas_data
        }, status=status.HTTP_200_OK)
