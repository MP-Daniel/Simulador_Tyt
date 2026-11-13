"""
================================================================================
INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO - UNIPUTUMAYO
FACULTAD DE INGENIERÍA - INGENIERÍA DE SISTEMAS (SEXTO SEMESTRE)
PROYECTO: SIMULADOR DE EVALUACIONES SABER TyT

SUITE DE PRUEBAS FUNCIONALES DE EXTREMO A EXTREMO (END-TO-END)
Verificación de las 4 Fases (A, B, C, D), los 26 pasos del Escenario
de Demostración Obligatoria y las 7 Pruebas Funcionales Mínimas.
================================================================================
"""

import os
import sys
import io
import json
from decimal import Decimal
from datetime import timedelta
import openpyxl

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from authentication.models import Usuario, Rol, Permiso
from cuestionarios.models import Cuestionario, CuestionarioPregunta
from banco_preguntas.models import Categoria, Pregunta, OpcionRespuesta, Importacion
from evaluaciones.models import Intento, RespuestaIntento, PeriodoAcademico, Curso, Matricula
from reportes.services.query_service import QueryService

def print_separator(title=""):
    print("\n" + "=" * 80)
    if title:
        print(f" {title.upper()}")
        print("=" * 80)

def run_tests():
    client = APIClient()
    print_separator("INICIANDO PRUEBAS INTEGRADORAS DE EXTREMO A EXTREMO - SABER TyT")

    # Limpieza de corridas previas para garantizar reproducibilidad e idempotencia
    Cuestionario.objects.filter(nombre__icontains="Evaluación Integradora").delete()
    Pregunta.objects.filter(enunciado__icontains="[Prueba Taller]").delete()
    Pregunta.objects.filter(enunciado__icontains="descuento?").delete()
    Pregunta.objects.filter(enunciado__icontains="beneficio primordial").delete()
    Pregunta.objects.filter(enunciado__icontains="queja?").delete()
    Pregunta.objects.filter(enunciado__icontains="engineering?").delete()
    
    # -------------------------------------------------------------------------
    # 0. VERIFICACIÓN Y PREPARACIÓN DE USUARIOS
    # -------------------------------------------------------------------------
    docente = Usuario.objects.get(username='docente')
    estudiante1 = Usuario.objects.get(username='estudiante1')
    estudiante2 = Usuario.objects.get(username='estudiante2')
    admin = Usuario.objects.get(username='admin')

    # Período y Curso de demostración
    periodo, _ = PeriodoAcademico.objects.get_or_create(
        anio=2026, nombre="2026-2",
        defaults={'activo': True}
    )
    curso_demo, _ = Curso.objects.get_or_create(
        nombre="Ingeniería de Sistemas 6A",
        periodo=periodo,
        defaults={'codigo': 'SIS-6A', 'programa': 'Ingeniería de Sistemas'}
    )
    Matricula.objects.get_or_create(estudiante=estudiante1, curso=curso_demo)
    Matricula.objects.get_or_create(estudiante=estudiante2, curso=curso_demo)

    # -------------------------------------------------------------------------
    # FASE A: ACCESO Y CONFIGURACIÓN DEL DOCENTE (Pasos 1-4, 20-21)
    # -------------------------------------------------------------------------
    print_separator("FASE A: ACCESO Y CONFIGURACIÓN DEL DOCENTE")

    # 1. Login Docente
    res_login = client.post('/api/auth/login/', {'username': 'docente', 'password': 'docente123'}, format='json')
    assert res_login.status_code == status.HTTP_200_OK, "Fallo login docente"
    docente_token = res_login.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {docente_token}')
    print("✓ Paso 1 & 20: Login Docente exitoso con JWT. Rol:", res_login.data['user']['rol']['nombre'])

    # 4. Validar Parámetros (Impedir cierre anterior a apertura, duración no positiva, intentos inválidos)
    ahora = timezone.now()
    fecha_apertura = ahora - timedelta(hours=1)
    fecha_cierre_invalida = ahora - timedelta(hours=2) # Error: cierre anterior

    res_inv_fecha = client.post('/api/cuestionarios/cuestionarios/', {
        'nombre': 'Cuestionario Fechas Inválidas',
        'asignatura': 'Razonamiento Cuantitativo',
        'fecha_apertura': fecha_apertura.isoformat(),
        'fecha_cierre': fecha_cierre_invalida.isoformat(),
        'tiempo_limite_minutos': 60,
        'intentos_permitidos': 2,
        'estado': 'borrador'
    }, format='json')
    assert res_inv_fecha.status_code == status.HTTP_400_BAD_REQUEST, "Debe rechazar cierre <= apertura"
    assert 'fecha_cierre' in str(res_inv_fecha.data), "Debe detallar error en fecha_cierre"
    print("✓ Paso 4 (Validación): Rechazado cierre anterior a apertura (Regla R01):", res_inv_fecha.data['fecha_cierre'][0])

    res_inv_dur = client.post('/api/cuestionarios/cuestionarios/', {
        'nombre': 'Cuestionario Duración Inválida',
        'asignatura': 'Razonamiento Cuantitativo',
        'fecha_apertura': ahora.isoformat(),
        'fecha_cierre': (ahora + timedelta(days=5)).isoformat(),
        'tiempo_limite_minutos': 0, # Error: duración no positiva
        'intentos_permitidos': 2,
        'estado': 'borrador'
    }, format='json')
    assert res_inv_dur.status_code == status.HTTP_400_BAD_REQUEST, "Debe rechazar duración <= 0"
    print("✓ Paso 4 (Validación): Rechazada duración no positiva (Regla R04):", res_inv_dur.data['tiempo_limite_minutos'][0])

    res_inv_int = client.post('/api/cuestionarios/cuestionarios/', {
        'nombre': 'Cuestionario Intentos Inválidos',
        'asignatura': 'Razonamiento Cuantitativo',
        'fecha_apertura': ahora.isoformat(),
        'fecha_cierre': (ahora + timedelta(days=5)).isoformat(),
        'tiempo_limite_minutos': 45,
        'intentos_permitidos': 0, # Error: intentos <= 0
        'estado': 'borrador'
    }, format='json')
    assert res_inv_int.status_code == status.HTTP_400_BAD_REQUEST, "Debe rechazar intentos <= 0"
    print("✓ Paso 4 (Validación): Rechazados intentos inválidos <= 0 (Regla R04):", res_inv_int.data['intentos_permitidos'][0])

    # 2 & 3. Crear cuestionario válido en estado Borrador con contraseña de acceso
    fecha_cierre_valida = ahora + timedelta(days=7)
    res_crear_quiz = client.post('/api/cuestionarios/cuestionarios/', {
        'nombre': 'Evaluación Integradora Saber TyT - Sexto Semestre',
        'asignatura': 'Competencias Genéricas Saber TyT',
        'descripcion': 'Evaluación funcional completa: Razonamiento Cuantitativo, Lectura Crítica, Ciudadanas e Inglés.',
        'clave_acceso': 'SaberTyT2026',
        'fecha_apertura': fecha_apertura.isoformat(),
        'fecha_cierre': fecha_cierre_valida.isoformat(),
        'tiempo_limite_minutos': 30,
        'intentos_permitidos': 1,
        'calificacion_maxima': '5.00',
        'calificacion_aprobacion': '3.00',
        'estado': 'borrador' # Estado inicial BORRADOR requerido por Fase A item 2
    }, format='json')
    assert res_crear_quiz.status_code == status.HTTP_201_CREATED, f"Error creando cuestionario: {res_crear_quiz.data}"
    cuestionario_id = res_crear_quiz.data['id']
    print(f"✓ Paso 2, 3 & 21: Cuestionario #{cuestionario_id} '{res_crear_quiz.data['nombre']}' creado.")
    print(f"  • Asignatura: {res_crear_quiz.data['asignatura']}")
    print(f"  • Estado Inicial: {res_crear_quiz.data['estado'].upper()} (Sin reactivos aún)")
    print(f"  • Contraseña configurada: {res_crear_quiz.data['clave_acceso']}")
    print(f"  • Tiempo límite: {res_crear_quiz.data['tiempo_limite_minutos']} min | Intentos: {res_crear_quiz.data['intentos_permitidos']}")

    # -------------------------------------------------------------------------
    # FASE B: PLANTILLA, BANCO DE PREGUNTAS E IMPORTACIÓN (Pasos 5-8, 22)
    # -------------------------------------------------------------------------
    print_separator("FASE B: PLANTILLA, BANCO DE PREGUNTAS E IMPORTACIÓN")

    # 5 & 6. Descargar plantilla Excel oficial
    res_descarga = client.get('/api/banco/descargar-plantilla/')
    assert res_descarga.status_code == status.HTTP_200_OK, "Fallo al descargar plantilla"
    wb_descargado = openpyxl.load_workbook(io.BytesIO(res_descarga.content))
    assert "Instrucciones" in wb_descargado.sheetnames, "Falta hoja de Instrucciones"
    assert "Plantilla_Preguntas" in wb_descargado.sheetnames, "Falta hoja Plantilla_Preguntas"
    ws_preg = wb_descargado["Plantilla_Preguntas"]
    headers_obtenidos = [ws_preg.cell(1, col).value for col in range(1, 13)]
    assert "enunciado" in headers_obtenidos, "Falta columna enunciado"
    assert "respuesta_correcta" in headers_obtenidos, "Falta columna respuesta_correcta"
    assert "tematica" in headers_obtenidos, "Falta columna tematica"
    print("✓ Paso 5, 6 & 22 (Descarga): Plantilla Excel verificada con 2 hojas ('Instrucciones' y 'Plantilla_Preguntas').")
    print(f"  Columnas verificadas: {headers_obtenidos}")

    # 7 & 8. Prueba Funcional de Rechazo: Archivo con campos vacíos o respuesta distinta de A-D (Caso Mínimo 2)
    wb_invalido = openpyxl.Workbook()
    ws_inv = wb_invalido.active
    ws_inv.title = "Plantilla_Preguntas"
    ws_inv.append(headers_obtenidos)
    # Fila 2: Enunciado vacío (Error 1)
    ws_inv.append(["Razonamiento Cuantitativo", "MULTIPLE", "Media", "", "", "OptA", "OptB", "OptC", "OptD", "A", "Retro", 2.50])
    # Fila 3: Respuesta correcta distinta de A-D ('Z') (Error 2)
    ws_inv.append(["Lectura Crítica", "MULTIPLE", "Alta", "", "¿Cuál es la idea principal del autor?", "OptA", "OptB", "OptC", "OptD", "Z", "Retro", 2.50])
    # Fila 4: Tipo binario con respuesta inválida ('X') (Error 3)
    ws_inv.append(["Competencias Ciudadanas", "VERDADERO_FALSO", "Media", "", "La Constitución garantiza la libertad de expresión.", "Verdadero", "Falso", "", "", "X", "Retro", 2.50])
    # Fila 5: Puntaje no positivo (0.00) (Error 4)
    ws_inv.append(["Inglés", "MULTIPLE", "Baja", "", "What is software testing?", "OptA", "OptB", "OptC", "OptD", "A", "Retro", 0.00])
    
    buf_inv = io.BytesIO()
    wb_invalido.save(buf_inv)
    buf_inv.seek(0)
    upload_inv = SimpleUploadedFile("preguntas_invalidas.xlsx", buf_inv.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    res_import_inv = client.post('/api/banco/importar-excel/', {'archivo': upload_inv}, format='multipart')
    assert res_import_inv.status_code == status.HTTP_400_BAD_REQUEST, "Debe rechazar archivo con errores"
    resumen_inv = res_import_inv.data['resumen']
    assert resumen_inv['errores'] == 4, f"Se esperaban 4 errores, se obtuvieron {resumen_inv['errores']}"
    print(f"✓ Paso 7, 8 (Caso Mínimo 2 - Rechazo): Se detectaron y rechazaron {resumen_inv['errores']} filas inválidas con mensajes claros:")
    for err in res_import_inv.data['errores_detalle']:
        print(f"  • Fila {err['fila']}: {err['error']}")

    # 7 & 8. Diligenciar plantilla válida y subir vinculándola directamente al cuestionario (Caso Mínimo 1)
    wb_valido = openpyxl.Workbook()
    ws_val = wb_valido.active
    ws_val.title = "Plantilla_Preguntas"
    ws_val.append(headers_obtenidos)

    reactivos_taller = [
        ["Razonamiento Cuantitativo", "MULTIPLE", "Media", "Un servidor cloud cuesta $100/mes.", "¿Cuánto se paga en 6 meses con 10% de descuento?", "$500", "$540", "$580", "$600", "B", "6 x 100 = 600 - 10% = 540", 2.50],
        ["Lectura Crítica", "MULTIPLE", "Alta", "El open source fomenta la soberanía digital comunitaria.", "¿Cuál es el beneficio primordial del software libre?", "Fomentar soberanía tecnológica comunitaria", "Crear monopolios cerrados", "Impedir ver el código", "Aumentar costo de licencias", "A", "El texto resalta la soberanía tecnológica", 2.50],
        ["Competencias Ciudadanas", "MULTIPLE", "Media", "Un ciudadano detecta posible sobrecosto en obras públicas.", "¿Ante qué entidad disciplinaria debe presentar la queja?", "Fiscalía General", "Procuraduría General de la Nación", "Defensoría del Pueblo", "Registraduría", "B", "La Procuraduría ejerce vigilancia disciplinaria", 2.50],
        ["Inglés", "MULTIPLE", "Baja", "Software documentation supports team maintainability.", "Why is system documentation vital in software engineering?", "To cause confusion", "To ensure maintainability and team collaboration", "To erase git history", "To add security bugs", "B", "Documentation promotes clarity and collaboration", 2.50]
    ]

    for fila in reactivos_taller:
        ws_val.append(fila)

    buf_val = io.BytesIO()
    wb_valido.save(buf_val)
    buf_val.seek(0)
    upload_val = SimpleUploadedFile("preguntas_oficiales_taller.xlsx", buf_val.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    res_import_val = client.post('/api/banco/importar-excel/', {
        'archivo': upload_val,
        'cuestionario_id': cuestionario_id
    }, format='multipart')
    assert res_import_val.status_code == status.HTTP_200_OK, f"Error importando válidas: {res_import_val.data}"
    resumen_val = res_import_val.data['resumen']
    assert resumen_val['validas'] == 4, f"Se esperaban 4 preguntas válidas, se obtuvieron {resumen_val['validas']}"
    assert resumen_val['cuestionario_asociado'] is not None, "Deben quedar asociadas al cuestionario"

    # Verificar en BD que las preguntas están asociadas al cuestionario
    quiz_obj = Cuestionario.objects.get(id=cuestionario_id)
    total_asociadas = quiz_obj.cuestionario_preguntas.count()
    assert total_asociadas == 4, f"Se esperaban 4 preguntas en el cuestionario, hay {total_asociadas}"
    print(f"✓ Paso 7, 8 & 22 (Caso Mínimo 1 - Éxito): Importación confirmada con {resumen_val['validas']} reactivos válidos.")
    print(f"  • Reactivos vinculados exitosamente a '{quiz_obj.nombre}': {total_asociadas} preguntas.")

    # -------------------------------------------------------------------------
    # FASE C: PUBLICACIÓN Y PRESENTACIÓN DEL ESTUDIANTE (Pasos 9-13, 23-24)
    # -------------------------------------------------------------------------
    print_separator("FASE C: PUBLICACIÓN Y PRESENTACIÓN DEL ESTUDIANTE")

    # 9 & 23. Activar el cuestionario (cambiar de Borrador a Disponible) y salir del docente
    res_activar = client.patch(f'/api/cuestionarios/cuestionarios/{cuestionario_id}/', {
        'estado': 'disponible',
        'activo': True
    }, format='json')
    assert res_activar.status_code == status.HTTP_200_OK, "Fallo al activar cuestionario"
    print(f"✓ Paso 9 & 23: Cuestionario #{cuestionario_id} publicado y habilitado en estado 'DISPONIBLE'.")

    # Cerrar sesión docente
    client.post('/api/auth/logout/')
    client.credentials() # Limpiar credenciales
    print("✓ Paso 9 & 23: Sesión docente cerrada.")

    # 10 & 24. Iniciar sesión como Estudiante 1
    res_login_est = client.post('/api/auth/login/', {'username': 'estudiante1', 'password': 'estudiante123'}, format='json')
    assert res_login_est.status_code == status.HTTP_200_OK, "Fallo login estudiante1"
    token_estudiante = res_login_est.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_estudiante}')
    print("✓ Paso 10 & 24: Login exitoso como Estudiante 1:", res_login_est.data['user']['first_name'])

    # Visualizar exclusivamente evaluaciones disponibles
    res_disp = client.get('/api/cuestionarios/disponibles/')
    assert res_disp.status_code == status.HTTP_200_OK, "Fallo al consultar disponibles"
    ids_disponibles = [q['id'] for q in res_disp.data]
    assert cuestionario_id in ids_disponibles, "El cuestionario activo debe estar disponible para el estudiante"
    
    # Comprobar que los cuestionarios en borrador o cerrados NO se muestran (Caso Mínimo 3)
    cuestionarios_no_disponibles = Cuestionario.objects.exclude(estado='disponible')
    for q_nodisp in cuestionarios_no_disponibles:
        assert q_nodisp.id not in ids_disponibles, f"Cuestionario {q_nodisp.id} en estado '{q_nodisp.estado}' no debe ser visible"
    print(f"✓ Paso 10 (Caso Mínimo 3): El estudiante visualiza únicamente los cuestionarios habilitados ({len(res_disp.data)} disponibles). Borradores y cerrados quedan estrictamente ocultos.")

    # 11. Validar Contraseña de Acceso al iniciar intento
    # Intento 1: Sin contraseña
    res_sin_pass = client.post('/api/evaluaciones/iniciar/', {'cuestionario_id': cuestionario_id}, format='json')
    assert res_sin_pass.status_code == status.HTTP_400_BAD_REQUEST, "Debe solicitar contraseña"
    assert res_sin_pass.data.get('requiere_clave') is True, "Debe indicar requiere_clave"
    print("✓ Paso 11: Bloqueo exitoso al intentar iniciar sin contraseña:", res_sin_pass.data['detail'])

    # Intento 2: Contraseña errónea
    res_pass_err = client.post('/api/evaluaciones/iniciar/', {
        'cuestionario_id': cuestionario_id,
        'clave_acceso': 'ClaveErroneaXYZ'
    }, format='json')
    assert res_pass_err.status_code == status.HTTP_400_BAD_REQUEST, "Debe rechazar contraseña incorrecta"
    print("✓ Paso 11: Bloqueo exitoso ante contraseña incorrecta:", res_pass_err.data['detail'])

    # Intento 3: Contraseña correcta -> Inicio exitoso del intento
    res_iniciar = client.post('/api/evaluaciones/iniciar/', {
        'cuestionario_id': cuestionario_id,
        'clave_acceso': 'SaberTyT2026'
    }, format='json')
    assert res_iniciar.status_code == status.HTTP_200_OK, f"Error iniciando con clave: {res_iniciar.data}"
    intento_id = res_iniciar.data['intento_id']
    preguntas_examen = res_iniciar.data['preguntas']
    assert len(preguntas_examen) == 4, "Debe traer las 4 preguntas"
    print(f"✓ Paso 11 & 24: Contraseña validada. Intento #{res_iniciar.data['numero_intento']} iniciado (ID: {intento_id}).")
    print(f"  • Temporizador asignado: {res_iniciar.data['cuestionario']['tiempo_limite_minutos']} minutos")
    print(f"  • Preguntas cargadas: {len(preguntas_examen)} reactivos con opciones A-D (sin exposición de claves)")

    # 12. Responder preguntas (3 respondidas con la clave correcta, 1 omitida a propósito para validar R09)
    respuestas_payload = {}
    for idx, p in enumerate(preguntas_examen):
        p_id = p['id']
        p_obj = Pregunta.objects.get(id=p_id)
        if idx < 3:
            correct_opt = p_obj.opciones.filter(es_correcta=True).first()
            respuestas_payload[str(p_id)] = correct_opt.id
        else:
            # 4ta pregunta queda intencionalmente OMITIDA (Regla R09)
            pass

    res_finalizar = client.post(f'/api/evaluaciones/intentos/{intento_id}/finalizar/', {
        'respuestas': respuestas_payload,
        'duracion_segundos': 540
    }, format='json')
    assert res_finalizar.status_code == status.HTTP_200_OK, f"Error finalizando intento: {res_finalizar.data}"
    
    # Verificación de calificación matemática:
    # 3 aciertos de 4 reactivos posibles = 7.50 / 10.00 pts -> Nota = (7.50 / 10.00) * 5.00 = 3.75 / 5.00
    calif_obtenida = Decimal(res_finalizar.data['calificacion'])
    assert calif_obtenida == Decimal('3.75'), f"Calificación esperada 3.75, obtenida: {calif_obtenida}"
    assert res_finalizar.data['aciertos'] == 3, "Aciertos esperados 3"
    assert res_finalizar.data['omitidas'] == 1, "Omitidas esperadas 1 (Regla R09)"
    assert res_finalizar.data['resultado'] == 'aprobado', "Debe ser aprobado (3.75 >= 3.00)"

    print("✓ Paso 12 & 24 (Caso Mínimo 5 - Entrega): Intento calificado de forma persistente y matemática:")
    print(f"  • Calificación Final: {calif_obtenida} / 5.00 ({res_finalizar.data['resultado'].upper()})")
    print(f"  • Aciertos: {res_finalizar.data['aciertos']} | Omitidas (Regla R09): {res_finalizar.data['omitidas']}")
    print(f"  • Puntaje: {res_finalizar.data['puntaje_obtenido']} / {res_finalizar.data['puntaje_total_posible']} pts")

    # Validar prevención de envíos duplicados (idempotencia)
    res_dup = client.post(f'/api/evaluaciones/intentos/{intento_id}/finalizar/', {
        'respuestas': respuestas_payload
    }, format='json')
    assert res_dup.status_code == status.HTTP_200_OK
    assert 'ya fue finalizado' in res_dup.data['detail'], "Debe bloquear re-envío duplicado"
    print("✓ Paso 12: Prevención de envíos duplicados verificada.")

    # Validar límite de intentos alcanzado (Caso Mínimo 4)
    # Dado que intentos_permitidos=1, un nuevo intento debe ser rechazado
    res_bloqueo_intentos = client.post('/api/evaluaciones/iniciar/', {
        'cuestionario_id': cuestionario_id,
        'clave_acceso': 'SaberTyT2026'
    }, format='json')
    assert res_bloqueo_intentos.status_code == status.HTTP_400_BAD_REQUEST, "Debe bloquear intento adicional"
    assert 'límite de intentos' in res_bloqueo_intentos.data['detail'].lower(), "Debe detallar límite alcanzado"
    print("✓ Paso 12 (Caso Mínimo 4 - Límite Intentos): Segundo intento bloqueado exitosamente:", res_bloqueo_intentos.data['detail'])

    # 13. Confirmación de entrega y revisión del estudiante
    res_revision = client.get(f'/api/evaluaciones/intentos/{intento_id}/revision/')
    assert res_revision.status_code == status.HTTP_200_OK, "Fallo al obtener revisión"
    assert len(res_revision.data['respuestas']) == 4, "Debe contener el detalle de los 4 reactivos"
    print("✓ Paso 13 & 24: Revisión pedagógica consultada con retroalimentaciones y claves formativas.")

    # Bloqueo entre estudiantes (Caso Mínimo 7 - Aislamiento)
    client.post('/api/auth/logout/')
    client.credentials()
    res_log2 = client.post('/api/auth/login/', {'username': 'estudiante2', 'password': 'estudiante123'}, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {res_log2.data["access"]}')
    res_intruso = client.get(f'/api/evaluaciones/intentos/{intento_id}/revision/')
    assert res_intruso.status_code == status.HTTP_403_FORBIDDEN, "Estudiante 2 no puede ver notas de Estudiante 1"
    print("✓ Paso 13 & Caso Mínimo 7: Aislamiento entre estudiantes verificado (403 Forbidden para estudiante ajeno).")

    # Intentar acceder a endpoint privado docente siendo estudiante (Caso Mínimo 7)
    res_est_admin = client.get('/api/reportes/indicadores/')
    assert res_est_admin.status_code == status.HTTP_403_FORBIDDEN, "Estudiante debe tener 403 en reportes docentes"
    print("✓ Caso Mínimo 7 (Restricción por rol): Estudiante bloqueado con 403 Forbidden en módulo docente.")

    # -------------------------------------------------------------------------
    # FASE D: CONSULTAS, RESULTADOS Y ANÁLISIS DOCENTE (Pasos 14-19, 25-26)
    # -------------------------------------------------------------------------
    print_separator("FASE D: CONSULTAS, RESULTADOS Y ANÁLISIS DOCENTE")

    # 14 & 25. Reingresar con rol Docente
    client.post('/api/auth/logout/')
    client.credentials()
    res_doc_relogin = client.post('/api/auth/login/', {'username': 'docente', 'password': 'docente123'}, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {res_doc_relogin.data["access"]}')
    print("✓ Paso 14 & 25: Docente reingresa al sistema.")

    # 15. Consultar los estudiantes que presentaron la evaluación
    res_todos_intentos = client.get(f'/api/evaluaciones/todos-los-intentos/?cuestionario={cuestionario_id}')
    assert res_todos_intentos.status_code == status.HTTP_200_OK
    assert len(res_todos_intentos.data) == 1, "Debe listar el intento de Estudiante 1"
    att_doc = res_todos_intentos.data[0]
    print(f"✓ Paso 15 & 25: Consulta de participantes en evaluación #{cuestionario_id}:")
    print(f"  • Estudiante: {att_doc['estudiante_nombre']} (@{att_doc['estudiante_username']})")
    print(f"  • Calificación: {att_doc['calificacion']} / 5.00 | Estado: {att_doc['resultado'].upper()}")
    print(f"  • Intentos consumidos: #{att_doc['numero_intento']}")

    # 16. Resumen estadístico: participantes, aprobados, reprobados, promedio
    indicadores = QueryService.calcular_indicadores(Intento.objects.filter(cuestionario_id=cuestionario_id, estado_intento='finalizado'))
    assert indicadores['estudiantes_evaluados'] == 1
    assert indicadores['aprobados'] == 1
    assert indicadores['reprobados'] == 0
    assert indicadores['calificacion_promedio'] == 3.75
    assert indicadores['porcentaje_aprobacion'] == 100.0
    print("✓ Paso 16 & 25 (Caso Mínimo 6 - Estadísticas):")
    print(f"  • Participantes: {indicadores['estudiantes_evaluados']}")
    print(f"  • Aprobados: {indicadores['aprobados']} ({indicadores['porcentaje_aprobacion']}%)")
    print(f"  • Reprobados: {indicadores['reprobados']}")
    print(f"  • Calificación Promedio: {indicadores['calificacion_promedio']} / 5.00")

    # 17. Identificar preguntas con mayor proporción de respuestas incorrectas y aciertos por pregunta
    filtros_quiz = {'cuestionario_id': cuestionario_id}
    # Obtener respuestas de este intento específico
    qs_intentos_quiz = Intento.objects.filter(cuestionario_id=cuestionario_id, estado_intento='finalizado')
    dificultad_items = QueryService.consulta_preguntas_dificultad({'cuestionario_id': cuestionario_id})
    print("✓ Paso 17 & 25: Análisis de dificultad por pregunta:")
    for d in dificultad_items:
        print(f"  • P#{d['pregunta_id']} [{d['eje_tematico']}] -> Total: {d['total_respuestas']}, Aciertos: {d['aciertos']}, Errores: {d['errores']}, % Acierto: {d['porcentaje_acierto']}%")

    # 18. Analizar el desempeño por eje o temática
    desempeno_ejes = QueryService.consulta_desempeno_ejes({'cuestionario_id': cuestionario_id})
    print("✓ Paso 18 & 25: Desempeño por eje temático Saber TyT:")
    for eje in desempeno_ejes:
        print(f"  • Eje '{eje['eje_tematico']}': {eje['aciertos']}/{eje['total_respondidas']} aciertos ({eje['porcentaje_acierto']}%)")

    # 19 & 26. Validación Final: Contrastar cálculos con respuestas guardadas
    intento_db = Intento.objects.get(id=intento_id)
    respuestas_db = RespuestaIntento.objects.filter(intento=intento_db)
    aciertos_db = respuestas_db.filter(es_acierto=True).count()
    omitidas_db = respuestas_db.filter(opcion_seleccionada__isnull=True).count()
    
    assert aciertos_db == intento_db.aciertos == 3, "Inconsistencia en aciertos"
    assert omitidas_db == intento_db.omitidas == 1, "Inconsistencia en omitidas"
    assert intento_db.calificacion == Decimal('3.75'), "Inconsistencia en nota final"
    print("✓ Paso 19 & 26 (Validación Final): Integridad de datos e invarianza matemática comprobadas.")
    print("  Todos los registros en BD concuerdan exactamente con las respuestas enviadas.")

    print_separator("¡TODAS LAS PRUEBAS FUNCIONALES DE EXTREMO A EXTREMO PASARON EXITOSAMENTE (100%)!")

if __name__ == '__main__':
    run_tests()
