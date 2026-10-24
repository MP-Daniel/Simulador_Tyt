import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from authentication.models import Permiso, Rol, Usuario
from banco_preguntas.models import Categoria, Pregunta, OpcionRespuesta
from cuestionarios.models import Cuestionario, CuestionarioPregunta


class Command(BaseCommand):
    help = 'Puebla la base de datos MySQL con roles, permisos, usuarios demo, preguntas y cuestionarios iniciales.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("==> Sembrando datos iniciales para el Simulador Saber TyT..."))

        # 1. Permisos del Sistema (Guía Parcial, Sec 2.1 y 2.2)
        permisos_def = [
            # Módulo Usuarios
            ('usuarios.administrar', 'Administrar Usuarios', 'Usuarios', 'Crear, consultar, editar y activar/desactivar cuentas de usuario'),
            # Módulo Roles
            ('roles.administrar', 'Administrar Roles y Permisos', 'Roles', 'Crear, editar, activar/desactivar roles personalizados y asignar permisos'),
            # Módulo Banco de Preguntas
            ('preguntas.gestionar', 'Gestionar Banco de Preguntas', 'Banco de Preguntas', 'Crear, consultar, editar y desactivar reactivos en el banco'),
            ('preguntas.importar', 'Importar Preguntas Excel', 'Banco de Preguntas', 'Carga masiva y validación fila por fila desde Excel'),
            # Módulo Cuestionarios
            ('cuestionarios.gestionar', 'Configurar Cuestionarios', 'Cuestionarios', 'Crear, editar, activar/desactivar cuestionarios y asignar preguntas'),
            ('cuestionarios.rendir', 'Presentar Evaluaciones', 'Cuestionarios', 'Iniciar, navegar y finalizar intentos de evaluación disponibles'),
            # Módulo Resultados
            ('resultados.consultar_propios', 'Consultar Calificaciones Propias', 'Resultados', 'Ver historial y revisiones de sus propios exámenes'),
            ('resultados.consultar_todos', 'Consultar Resultados Globales', 'Resultados', 'Ver informes, intentos y notas de todos los estudiantes'),
        ]

        permisos_map = {}
        for codigo, nombre, modulo, desc in permisos_def:
            p, created = Permiso.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'modulo': modulo, 'descripcion': desc}
            )
            permisos_map[codigo] = p

        self.stdout.write(self.style.SUCCESS(f"✓ {len(permisos_map)} permisos del sistema registrados."))

        # 2. Roles Predeterminados y Rol Personalizado Demo (Sec 2.2)
        # Rol Administrador (Predeterminado)
        rol_admin, _ = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Control total del sistema: usuarios, roles, banco, cuestionarios e informes.',
                'es_predeterminado': True,
                'activo': True
            }
        )
        rol_admin.permisos.set(list(permisos_map.values()))

        # Rol Estudiante (Predeterminado)
        rol_estudiante, _ = Rol.objects.get_or_create(
            nombre='Estudiante',
            defaults={
                'descripcion': 'Presentación de cuestionarios habilitados y consulta de notas propias.',
                'es_predeterminado': True,
                'activo': True
            }
        )
        rol_estudiante.permisos.set([
            permisos_map['cuestionarios.rendir'],
            permisos_map['resultados.consultar_propios'],
        ])

        # Rol Personalizado: Docente Evaluador (Ejemplo explícito del enunciado del parcial, Sec 2.2)
        rol_docente, _ = Rol.objects.get_or_create(
            nombre='Docente Evaluador',
            defaults={
                'descripcion': 'Gestor académico: crea preguntas, cuestionarios e importa desde Excel sin gestionar usuarios.',
                'es_predeterminado': False,
                'activo': True
            }
        )
        rol_docente.permisos.set([
            permisos_map['preguntas.gestionar'],
            permisos_map['preguntas.importar'],
            permisos_map['cuestionarios.gestionar'],
            permisos_map['resultados.consultar_todos'],
            permisos_map['resultados.consultar_propios'],
        ])

        self.stdout.write(self.style.SUCCESS("✓ Roles configurados: Administrador, Estudiante y Docente Evaluador."))

        # 3. Usuarios Demo
        # Superuser / Administrador
        if not Usuario.objects.filter(username='admin').exists():
            admin_user = Usuario.objects.create_superuser(
                username='admin',
                email='admin@uniputumayo.edu.co',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                codigo_estudiantil='ADM-001',
                programa_academico='Ingeniería de Sistemas',
                rol=rol_admin
            )
            self.stdout.write(self.style.SUCCESS("✓ Usuario 'admin' (password: admin123) creado."))
        else:
            admin_user = Usuario.objects.get(username='admin')
            admin_user.rol = rol_admin
            admin_user.save()

        # Docente Evaluador
        if not Usuario.objects.filter(username='docente').exists():
            docente_user = Usuario.objects.create_user(
                username='docente',
                email='docente@uniputumayo.edu.co',
                password='docente123',
                first_name='Prof. Carlos',
                last_name='Rodríguez',
                codigo_estudiantil='DOC-102',
                programa_academico='Ingeniería de Sistemas',
                rol=rol_docente
            )
            self.stdout.write(self.style.SUCCESS("✓ Usuario 'docente' (password: docente123) creado."))

        # Estudiante 1 (Activo)
        if not Usuario.objects.filter(username='estudiante1').exists():
            est1 = Usuario.objects.create_user(
                username='estudiante1',
                email='jperez@uniputumayo.edu.co',
                password='estudiante123',
                first_name='Juan David',
                last_name='Pérez',
                codigo_estudiantil='SIS-2026-01',
                programa_academico='Ingeniería de Sistemas',
                rol=rol_estudiante
            )
            self.stdout.write(self.style.SUCCESS("✓ Usuario 'estudiante1' (password: estudiante123) creado."))

        # Estudiante 2 (Activo)
        if not Usuario.objects.filter(username='estudiante2').exists():
            est2 = Usuario.objects.create_user(
                username='estudiante2',
                email='mgomez@uniputumayo.edu.co',
                password='estudiante123',
                first_name='María Paula',
                last_name='Gómez',
                codigo_estudiantil='SIS-2026-02',
                programa_academico='Ingeniería de Sistemas',
                rol=rol_estudiante
            )
            self.stdout.write(self.style.SUCCESS("✓ Usuario 'estudiante2' (password: estudiante123) creado."))

        # Estudiante Desactivado (Para demostración de control de cuentas desactivadas - Sec 2.1)
        if not Usuario.objects.filter(username='inactivo').exists():
            inactivo_user = Usuario.objects.create_user(
                username='inactivo',
                email='inactivo@uniputumayo.edu.co',
                password='inactivo123',
                first_name='Estudiante',
                last_name='Suspendido',
                codigo_estudiantil='SIS-2026-99',
                programa_academico='Ingeniería de Sistemas',
                rol=rol_estudiante,
                is_active=False
            )
            self.stdout.write(self.style.SUCCESS("✓ Usuario 'inactivo' (cuenta desactivada, password: inactivo123) creado."))

        # 4. Categorías / Competencias
        cats_data = [
            ("Razonamiento Cuantitativo", "Resolución de problemas numéricos, modelado matemático y análisis de datos."),
            ("Lectura Crítica", "Comprensión semántica, análisis de argumentos y juicio crítico de textos."),
            ("Competencias Ciudadanas", "Conocimiento constitucional, mecanismos de participación y convivencia social."),
            ("Inglés", "Comprensión lectora y estructuras gramaticales en lengua extranjera nivel B1."),
        ]
        cat_objs = {}
        for nom, desc in cats_data:
            c, _ = Categoria.objects.get_or_create(nombre=nom, defaults={'descripcion': desc, 'activo': True})
            cat_objs[nom] = c

        self.stdout.write(self.style.SUCCESS("✓ Categorías Saber TyT registradas."))

        # 5. Preguntas del Banco con Opciones (Reglas R05 y R06)
        preguntas_seed = [
            {
                'categoria': cat_objs["Razonamiento Cuantitativo"],
                'tipo': 'MULTIPLE',
                'texto_base': 'En una empresa de software se requiere determinar el costo de producción para el despliegue de infraestructura en la nube.',
                'enunciado': '¿Si un servidor en la nube cuesta $100 al mes, cuánto se pagará en 6 meses con un 10% de descuento?',
                'puntaje': Decimal('2.50'),
                'retroalimentacion': 'El costo sin descuento es 6 x $100 = $600. El 10% de 600 es $60. Por tanto, 600 - 60 = $540.',
                'opciones': [
                    ('A', '$500', False),
                    ('B', '$540', True),
                    ('C', '$580', False),
                    ('D', '$600', False),
                ]
            },
            {
                'categoria': cat_objs["Lectura Crítica"],
                'tipo': 'VERDADERO_FALSO',
                'texto_base': None,
                'enunciado': 'En las pruebas Saber TyT, el componente de lectura crítica evalúa prioritariamente la capacidad de memorizar fechas y nombres de autores.',
                'puntaje': Decimal('2.50'),
                'retroalimentacion': 'Es falso. Evalúa la comprensión semántica, la jerarquía de ideas y el análisis de posturas, no la memorización mecánica.',
                'opciones': [
                    ('V', 'Verdadero', False),
                    ('F', 'Falso', True),
                ]
            },
            {
                'categoria': cat_objs["Competencias Ciudadanas"],
                'tipo': 'MULTIPLE',
                'texto_base': 'La Constitución Política de Colombia de 1991 consagra derechos fundamentales y mecanismos de protección sumaria.',
                'enunciado': '¿Cuál es el mecanismo judicial expedito para la protección inmediata de los derechos constitucionales fundamentales amenazados o vulnerados?',
                'puntaje': Decimal('2.50'),
                'retroalimentacion': 'El artículo 86 de la Constitución consagra la Acción de Tutela para la protección inmediata de derechos fundamentales.',
                'opciones': [
                    ('A', 'Acción de Cumplimiento', False),
                    ('B', 'Acción Popular', False),
                    ('C', 'Acción de Tutela', True),
                    ('D', 'Habeas Data', False),
                ]
            },
            {
                'categoria': cat_objs["Inglés"],
                'tipo': 'MULTIPLE',
                'texto_base': None,
                'enunciado': "Choose the correct sentence to complete the idea: 'Software engineers usually _______ database schemas before writing code.'",
                'puntaje': Decimal('2.50'),
                'retroalimentacion': "Con el sujeto plural 'Software engineers', en presente simple se utiliza la forma base 'design'.",
                'opciones': [
                    ('A', 'designs', False),
                    ('B', 'design', True),
                    ('C', 'designing', False),
                    ('D', 'designed', False),
                ]
            },
            {
                'categoria': cat_objs["Razonamiento Cuantitativo"],
                'tipo': 'MULTIPLE',
                'texto_base': 'Un algoritmo procesa una lista de N elementos con complejidad cuadrática O(N²).',
                'enunciado': 'Si para 10 elementos tarda 2 segundos, ¿cuántos segundos tardará para procesar 20 elementos?',
                'puntaje': Decimal('2.50'),
                'retroalimentacion': 'Al duplicar N de 10 a 20, con O(N²) el tiempo se multiplica por 2² = 4. Por ende, 2 s x 4 = 8 segundos.',
                'opciones': [
                    ('A', '4 segundos', False),
                    ('B', '6 segundos', False),
                    ('C', '8 segundos', True),
                    ('D', '10 segundos', False),
                ]
            },
        ]

        preguntas_creadas = []
        for p_data in preguntas_seed:
            opciones = p_data.pop('opciones')
            pregunta, _ = Pregunta.objects.get_or_create(
                enunciado=p_data['enunciado'],
                defaults=p_data
            )
            for letra, texto, es_corr in opciones:
                OpcionRespuesta.objects.get_or_create(
                    pregunta=pregunta,
                    letra=letra,
                    defaults={'texto': texto, 'es_correcta': es_corr}
                )
            preguntas_creadas.append(pregunta)

        self.stdout.write(self.style.SUCCESS(f"✓ {len(preguntas_creadas)} preguntas con opciones sembradas en el banco."))

        # 6. Cuestionarios de Prueba
        ahora = timezone.now()

        # Cuestionario 1: Disponible (Activo ahora)
        c1, _ = Cuestionario.objects.get_or_create(
            nombre='Simulacro Diagnóstico Saber TyT 2026-II',
            defaults={
                'descripcion': 'Evaluación diagnóstica integral de competencias genéricas para estudiantes de Ingeniería de Sistemas.',
                'fecha_apertura': ahora - timedelta(days=5),
                'fecha_cierre': ahora + timedelta(days=30),
                'tiempo_limite_minutos': 60,
                'intentos_permitidos': 2,
                'calificacion_maxima': Decimal('5.00'),
                'calificacion_aprobacion': Decimal('3.00'),
                'mezclar_preguntas': True,
                'mezclar_respuestas': True,
                'permitir_revision': True,
                'estado': 'disponible',
                'activo': True
            }
        )
        for idx, p in enumerate(preguntas_creadas, 1):
            CuestionarioPregunta.objects.get_or_create(
                cuestionario=c1,
                pregunta=p,
                defaults={'puntaje': p.puntaje, 'orden': idx}
            )

        # Cuestionario 2: Programado (Para demostrar bloqueo de inicio antes de apertura - R08)
        c2, _ = Cuestionario.objects.get_or_create(
            nombre='Simulacro de Competencias Ciudadanas e Inglés',
            defaults={
                'descripcion': 'Evaluación programada para próximas fechas. Aún no disponible para presentación.',
                'fecha_apertura': ahora + timedelta(days=10),
                'fecha_cierre': ahora + timedelta(days=25),
                'tiempo_limite_minutos': 45,
                'intentos_permitidos': 1,
                'calificacion_maxima': Decimal('5.00'),
                'calificacion_aprobacion': Decimal('3.00'),
                'mezclar_preguntas': True,
                'mezclar_respuestas': True,
                'permitir_revision': True,
                'estado': 'programado',
                'activo': True
            }
        )

        # Cuestionario 3: Cerrado (Para demostrar bloqueo de inicio tras cierre - R08)
        c3, _ = Cuestionario.objects.get_or_create(
            nombre='Prueba Piloto Saber TyT (Semestre Anterior)',
            defaults={
                'descripcion': 'Examen de práctica del semestre anterior. Cerrado para nuevas presentaciones.',
                'fecha_apertura': ahora - timedelta(days=60),
                'fecha_cierre': ahora - timedelta(days=30),
                'tiempo_limite_minutos': 30,
                'intentos_permitidos': 1,
                'calificacion_maxima': Decimal('5.00'),
                'calificacion_aprobacion': Decimal('3.00'),
                'mezclar_preguntas': False,
                'mezclar_respuestas': False,
                'permitir_revision': False,
                'estado': 'cerrado',
                'activo': True
            }
        )

        self.stdout.write(self.style.SUCCESS("✓ Cuestionarios creados: Disponible, Programado y Cerrado."))
        self.stdout.write(self.style.SUCCESS("==> ¡Siembra de datos completada con éxito en MySQL/MariaDB!"))
