import os
import sys
import json
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from authentication.models import Rol, Permiso
from cuestionarios.models import Cuestionario
from evaluaciones.models import Intento

Usuario = get_user_model()
client = APIClient()

# Limpiar intentos previos de pruebas para permitir ejecuciones idempotentes
Intento.objects.filter(estudiante__username__in=['estudiante1', 'estudiante2']).delete()
Rol.objects.filter(nombre='Tutor Auxiliar').delete()

print("=" * 75)
print("VERIFICACIÓN AUTOMATIZADA DE SEGURIDAD JWT, ROLES Y EVALUACIÓN SABER TYT")
print("=" * 75)

# 1. Prueba de Login Administrador (Generación de Tokens JWT)
res_admin = client.post('/api/auth/login/', {
    'username': 'admin',
    'password': 'admin123'
}, format='json')

assert res_admin.status_code == 200, f"Error en login admin: {res_admin.data}"
tokens_admin = res_admin.data
assert 'access' in tokens_admin and 'refresh' in tokens_admin
print("✓ 1. Login Administrador exitoso. Tokens JWT (access & refresh) generados.")

# 2. Prueba de Control de Cuentas Desactivadas (Sec 2.1)
res_inactivo = client.post('/api/auth/login/', {
    'username': 'inactivo',
    'password': 'inactivo123'
}, format='json')
assert res_inactivo.status_code in [400, 401], "Fallo: Cuenta desactivada pudo iniciar sesión."
print("✓ 2. Control de cuentas desactivadas verificado: Usuario inactivo rechazado por JWT.")

# 3. Login de Estudiante
res_est1 = client.post('/api/auth/login/', {
    'username': 'estudiante1',
    'password': 'estudiante123'
}, format='json')
assert res_est1.status_code == 200
tokens_est1 = res_est1.data
token_est1 = tokens_est1['access']
print("✓ 3. Login de Estudiante 1 exitoso. Token JWT emitido.")

# 4. Verificación de claims y endpoint /api/auth/me/
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_est1}')
res_me = client.get('/api/auth/me/')
assert res_me.status_code == 200
assert res_me.data['username'] == 'estudiante1'
assert 'cuestionarios.rendir' in res_me.data['permisos']
print(f"✓ 4. Endpoint /api/auth/me/ validó token JWT para {res_me.data['full_name']}.")

# 5. Restricción en Django: Estudiante intenta administrar usuarios (403 Forbidden)
res_unauthorized = client.post('/api/auth/usuarios/', {
    'username': 'hacker',
    'password': 'password123'
}, format='json')
assert res_unauthorized.status_code == 403, "Fallo: Estudiante pudo acceder a administración de usuarios."
print("✓ 5. Restricción verificada en Django: Estudiante recibió 403 Forbidden al intentar administrar usuarios.")

# 6. Blindaje de Negocio: Administrador intenta iniciar examen oficial -> 403 Forbidden
cuestionario = Cuestionario.objects.filter(estado='disponible', cuestionario_preguntas__isnull=False).first()
assert cuestionario is not None, "Debe existir un cuestionario con preguntas en BD."

client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens_admin["access"]}')
res_admin_start = client.post('/api/evaluaciones/iniciar/', {
    'cuestionario_id': cuestionario.id
}, format='json')
assert res_admin_start.status_code == 403, "Fallo: Administrador no debe poder presentar examen oficial."
assert "Solo los usuarios con rol 'Estudiante' pueden presentar evaluaciones oficiales" in res_admin_start.data['error']
print("✓ 6. Blindaje de negocio verificado: Administrador bloqueado con 403 Forbidden al intentar rendir examen.")

# 7. Blindaje de Negocio: Docente Evaluador intenta iniciar examen oficial -> 403 Forbidden
res_doc = client.post('/api/auth/login/', {'username': 'docente', 'password': 'docente123'}, format='json')
assert res_doc.status_code == 200
token_doc = res_doc.data['access']
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_doc}')

res_doc_start = client.post('/api/evaluaciones/iniciar/', {
    'cuestionario_id': cuestionario.id
}, format='json')
assert res_doc_start.status_code == 403, "Fallo: Docente no debe poder presentar examen oficial."
assert "Solo los usuarios con rol 'Estudiante' pueden presentar evaluaciones oficiales" in res_doc_start.data['error']
print("✓ 7. Blindaje de negocio verificado: Docente bloqueado con 403 Forbidden al intentar rendir examen.")

# 8. Modo Previsualización (Sandbox): Docente y Administrador pueden previsualizar examen sin generar intento
intentos_antes = Intento.objects.count()
res_preview = client.get(f'/api/cuestionarios/{cuestionario.id}/previsualizar/')
assert res_preview.status_code == 200, f"Error en previsualización: {res_preview.data}"
assert res_preview.data['es_sandbox'] is True
assert len(res_preview.data['preguntas']) > 0
# Verificar que las claves correctas y retroalimentaciones sí son visibles en previsualización
p_sample = res_preview.data['preguntas'][0]
assert any(opt.get('es_correcta') is True for opt in p_sample['opciones'])
assert p_sample.get('retroalimentacion') is not None
intentos_despues = Intento.objects.count()
assert intentos_antes == intentos_despues, "La previsualización Sandbox NO debe generar ningún intento en la base de datos."
print(f"✓ 8. Modo Previsualización (Sandbox) verificado para Docentes: {len(res_preview.data['preguntas'])} reactivos con claves, 0 intentos en BD.")

# 9. Seguridad: Estudiante intenta acceder a Previsualización (Sandbox) -> 403 Forbidden
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_est1}')
res_est_preview = client.get(f'/api/cuestionarios/{cuestionario.id}/previsualizar/')
assert res_est_preview.status_code == 403, "Fallo: Estudiante no debe poder acceder a previsualización de docentes."
print("✓ 9. Protección de Sandbox verificada: Estudiante recibió 403 Forbidden al intentar previsualizar.")

# 10. Estudiante matriculado inicia examen oficial (Sec 2.5)
res_inicio = client.post('/api/evaluaciones/iniciar/', {
    'cuestionario_id': cuestionario.id
}, format='json')
assert res_inicio.status_code == 200, f"Error iniciando examen: {res_inicio.data}"
inicio_data = res_inicio.data
intento_id = inicio_data['intento_id']
preguntas = inicio_data['preguntas']
assert len(preguntas) > 0

# Verificar seguridad: NO exponer 'es_correcta' ni 'retroalimentacion' durante el examen oficial
for p in preguntas:
    assert 'retroalimentacion' not in p or p.get('retroalimentacion') is None
    for opt in p['opciones']:
        assert 'es_correcta' not in opt
print("✓ 10. Presentación del examen segura: Las opciones NO exponen 'es_correcta' ni retroalimentación.")

# 11. Finalizar y calificar automáticamente en Django (Sec 2.5)
from banco_preguntas.models import Pregunta
respuestas_payload = {}
p0_obj = Pregunta.objects.get(id=preguntas[0]['id'])
p1_obj = Pregunta.objects.get(id=preguntas[1]['id'])

respuestas_payload[str(p0_obj.id)] = p0_obj.opcion_correcta.letra
respuestas_payload[str(p1_obj.id)] = p1_obj.opcion_correcta.letra

res_fin = client.post(f'/api/evaluaciones/intentos/{intento_id}/finalizar/', {
    'respuestas': respuestas_payload,
    'duracion_segundos': 300
}, format='json')

assert res_fin.status_code == 200, f"Error finalizando intento: {res_fin.data}"
fin_data = res_fin.data
assert fin_data['aciertos'] == 2, f"Esperado 2 aciertos, obtenido {fin_data['aciertos']}"
assert fin_data['omitidas'] == len(preguntas) - 2, f"Esperado {len(preguntas) - 2} omitidas, obtenido {fin_data['omitidas']}"
nota_calc = float(fin_data['calificacion'])
print(f"✓ 11. Calificación automática en Django: Nota calculada: {nota_calc} / 5.00 ({fin_data['resultado']}).")
print(f"      Aciertos: {fin_data['aciertos']}, Omitidas (R09): {fin_data['omitidas']}.")

# 12. Seguridad entre estudiantes: Estudiante 2 intenta consultar el intento de Estudiante 1 (Sec 2.5)
res_est2 = client.post('/api/auth/login/', {'username': 'estudiante2', 'password': 'estudiante123'}, format='json')
token_est2 = res_est2.data['access']
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_est2}')

res_espionaje = client.get(f'/api/evaluaciones/intentos/{intento_id}/revision/')
assert res_espionaje.status_code == 403, "Fallo: Estudiante 2 pudo acceder al examen de Estudiante 1."
print("✓ 12. Aislamiento entre estudiantes verificado: Estudiante 2 recibió 403 Forbidden al consultar intento ajeno.")

# 13. Estudiante 1 consulta su propia revisión (Permitido)
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_est1}')
res_revision_propia = client.get(f'/api/evaluaciones/intentos/{intento_id}/revision/')
assert res_revision_propia.status_code == 200
print("✓ 13. Estudiante 1 consultó exitosamente su propia revisión con retroalimentación pedagógica.")

# 14. Administrador crea un rol configurable con permisos atómicos (Sec 2.2)
client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens_admin["access"]}')
perm_gestionar_preguntas = Permiso.objects.get(codigo='preguntas.gestionar')
perm_gestionar_cuestionarios = Permiso.objects.get(codigo='cuestionarios.gestionar')

res_crear_rol = client.post('/api/auth/roles/', {
    'nombre': 'Tutor Auxiliar',
    'descripcion': 'Rol personalizado para apoyo en reactivos.',
    'activo': True,
    'permisos_ids': [perm_gestionar_preguntas.id, perm_gestionar_cuestionarios.id]
}, format='json')
assert res_crear_rol.status_code == 201, f"Error creando rol: {res_crear_rol.data}"
print(f"✓ 14. Gestión de roles configurables: Rol '{res_crear_rol.data['nombre']}' creado con permisos atómicos.")

print("=" * 75)
print("¡TODAS LAS 14 PRUEBAS DE SEGURIDAD JWT, ROLES Y BLINDAJE PASARON EXITOSAMENTE!")
print("=" * 75)
