"""
Comando para poblar la estructura académica (períodos, cursos, matrículas)
e intentos evaluativos realistas en los 4 ejes temáticos Saber TyT.
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from authentication.models import Usuario, Rol
from banco_preguntas.models import Categoria, Pregunta, OpcionRespuesta
from cuestionarios.models import Cuestionario, CuestionarioPregunta
from evaluaciones.models import PeriodoAcademico, Curso, Matricula, Intento, RespuestaIntento


class Command(BaseCommand):
    help = 'Puebla períodos académicos, cursos, matrículas e intentos de prueba para reportes Saber TyT'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Inicializando datos académicos para el Módulo de Reportes...'))

        # 1. PERÍODOS ACADÉMICOS
        p_2026_2, _ = PeriodoAcademico.objects.get_or_create(
            anio=2026, nombre='2026-2', defaults={'activo': True}
        )
        p_2026_1, _ = PeriodoAcademico.objects.get_or_create(
            anio=2026, nombre='2026-1', defaults={'activo': True}
        )
        p_2025_2, _ = PeriodoAcademico.objects.get_or_create(
            anio=2025, nombre='2025-2', defaults={'activo': True}
        )
        self.stdout.write(self.style.SUCCESS('✓ Períodos académicos configurados (2025-2, 2026-1, 2026-2).'))

        # 2. CURSOS / GRUPOS
        curso_6a_2026, _ = Curso.objects.get_or_create(
            nombre='Sexto A', periodo=p_2026_2,
            defaults={'codigo': 'SIS-6A-2026-2', 'programa': 'Ingeniería de Sistemas'}
        )
        curso_6b_2026, _ = Curso.objects.get_or_create(
            nombre='Sexto B', periodo=p_2026_2,
            defaults={'codigo': 'SIS-6B-2026-2', 'programa': 'Ingeniería de Sistemas'}
        )
        curso_6a_antiguo, _ = Curso.objects.get_or_create(
            nombre='Sexto A', periodo=p_2026_1,
            defaults={'codigo': 'SIS-6A-2026-1', 'programa': 'Ingeniería de Sistemas'}
        )
        self.stdout.write(self.style.SUCCESS('✓ Cursos / Grupos configurados (Sexto A y Sexto B).'))

        # 3. ESTUDIANTES Y MATRÍCULAS
        rol_estudiante = Rol.objects.filter(nombre='Estudiante').first()

        def crear_o_obtener_estudiante(username, first_name, last_name, codigo):
            u, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@uniputumayo.edu.co',
                    'codigo_estudiantil': codigo,
                    'rol': rol_estudiante,
                    'is_active': True
                }
            )
            if created:
                u.set_password('Estudiante.2026*')
                u.save()
            return u

        est1 = crear_o_obtener_estudiante('estudiante1', 'Juan David', 'Pérez Gómez', 'SIS-2026-01')
        est2 = crear_o_obtener_estudiante('estudiante2', 'María Camila', 'López Restrepo', 'SIS-2026-02')
        est3 = crear_o_obtener_estudiante('estudiante3_sofia', 'Sofía', 'Andrade Caicedo', 'SIS-2026-03')
        est4 = crear_o_obtener_estudiante('estudiante4_carlos', 'Carlos', 'Muñoz Benavides', 'SIS-2026-04')
        est5 = crear_o_obtener_estudiante('estudiante5_valeria', 'Valeria', 'Guerrero Silva', 'SIS-2026-05')

        # Matrículas
        Matricula.objects.get_or_create(estudiante=est1, curso=curso_6a_2026)
        Matricula.objects.get_or_create(estudiante=est3, curso=curso_6a_2026)
        Matricula.objects.get_or_create(estudiante=est2, curso=curso_6b_2026)
        Matricula.objects.get_or_create(estudiante=est4, curso=curso_6b_2026)
        Matricula.objects.get_or_create(estudiante=est5, curso=curso_6a_antiguo)
        self.stdout.write(self.style.SUCCESS('✓ Estudiantes y matrículas vinculadas.'))

        # 4. ACTUALIZAR CURSOS EN INTENTOS HISTÓRICOS
        for intento in Intento.objects.filter(curso__isnull=True):
            mat = intento.estudiante.matriculas.first()
            if mat:
                intento.curso = mat.curso
                intento.save(update_fields=['curso'])

        # 5. CUESTIONARIO BASE
        cuestionario = Cuestionario.objects.first()
        if not cuestionario:
            self.stdout.write(self.style.WARNING('No se encontró cuestionario para generar simulacros.'))
            return

        preguntas = list(Pregunta.objects.filter(activo=True).select_related('categoria').prefetch_related('opciones'))

        # 6. GENERAR INTENTOS REALISTAS CON CALIFICACIÓN Y RESPUESTAS POR EJE
        estudiantes_data = [
            (est1, curso_6a_2026, 4.20, 'aprobado', 4, 1, 0),
            (est2, curso_6b_2026, 3.60, 'aprobado', 3, 2, 0),
            (est3, curso_6a_2026, 4.80, 'aprobado', 5, 0, 0),
            (est4, curso_6b_2026, 2.40, 'reprobado', 2, 3, 0),
            (est5, curso_6a_antiguo, 3.80, 'aprobado', 4, 1, 0),
            (est1, curso_6a_2026, 2.00, 'reprobado', 2, 2, 1), # Segundo intento de Juan David
            (est2, curso_6b_2026, 4.50, 'aprobado', 4, 1, 0), # Segundo intento de María Camila
        ]

        now = timezone.now()

        for idx, (est, curso, calif, resultado, aciertos_n, errores_n, omitidas_n) in enumerate(estudiantes_data, 1):
            fecha_i = now - timedelta(days=idx * 2, hours=3)
            fecha_f = fecha_i + timedelta(minutes=45)

            intento, created = Intento.objects.get_or_create(
                cuestionario=cuestionario,
                estudiante=est,
                numero_intento=1 if idx <= 5 else 2,
                defaults={
                    'curso': curso,
                    'fecha_inicio': fecha_i,
                    'fecha_fin': fecha_f,
                    'duracion_segundos': 2700,
                    'puntaje_obtenido': Decimal(str(calif)),
                    'puntaje_total_posible': Decimal('5.00'),
                    'calificacion': Decimal(str(calif)),
                    'estado_intento': 'finalizado',
                    'resultado': resultado,
                    'total_preguntas': len(preguntas[:5]),
                    'aciertos': aciertos_n,
                    'errores': errores_n,
                    'omitidas': omitidas_n
                }
            )

            if not created and intento.curso is None:
                intento.curso = curso
                intento.save()

            # Respuestas a cada pregunta para estadísticas de ejes temáticos
            for p_idx, p in enumerate(preguntas[:5]):
                opciones = list(p.opciones.all())
                opc_correcta = next((o for o in opciones if o.es_correcta), None)
                opc_incorrecta = next((o for o in opciones if not o.es_correcta), None)

                es_acierto = (p_idx < aciertos_n)
                es_omitida = (p_idx >= aciertos_n + errores_n)

                if es_omitida:
                    opcion_sel = None
                    pts = Decimal('0.00')
                elif es_acierto:
                    opcion_sel = opc_correcta
                    pts = Decimal('1.00')
                else:
                    opcion_sel = opc_incorrecta or opc_correcta
                    pts = Decimal('0.00')

                RespuestaIntento.objects.update_or_create(
                    intento=intento,
                    pregunta=p,
                    defaults={
                        'opcion_seleccionada': opcion_sel,
                        'es_acierto': es_acierto and not es_omitida,
                        'puntaje_obtenido': pts,
                        'marcada_revision': False
                    }
                )

        self.stdout.write(self.style.SUCCESS(
            f'✓ {len(estudiantes_data)} intentos evaluativos sincronizados con respuestas por eje temático.'
        ))
        self.stdout.write(self.style.SUCCESS('¡Poblado de datos de reportes completado exitosamente!'))
