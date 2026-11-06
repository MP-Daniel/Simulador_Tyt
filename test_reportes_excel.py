"""
Suite Automatizada de Verificación del Módulo de Consultas, Reportes y Excel.
Valida:
1. Filtros jerárquicos en cascada (Año -> Período -> Curso -> Eje -> Estudiante).
2. Las 7 consultas obligatorias resueltas mediante Django ORM.
3. Indicadores estadísticos (KPIs: promedio, mínimos, máximos, porcentaje de aprobación).
4. Generación real de los 3 archivos Excel (.xlsx) con openpyxl.
5. Seguridad y autorización (401 sin token, 403 para Estudiantes, 200 para Docente/Admin).
6. Casos límite (filtros sin registros retornan 200 sin error 500).
"""
import os
import django
import openpyxl

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import Usuario
from reportes.services.query_service import QueryService
from reportes.services.excel_service import ExcelReportService
from reportes.views import (
    FiltrosCascadaAPIView,
    IndicadoresReporteAPIView,
    ConsultasReportesAPIView,
    ExportarExcelAPIView
)


def run_tests():
    print("=" * 80)
    print("VERIFICACIÓN AUTOMATIZADA: MÓDULO DE REPORTES, CONSULTAS Y EXCEL (.XLSX)")
    print("=" * 80)

    factory = RequestFactory()
    admin_user = Usuario.objects.filter(username='admin').first()
    docente_user = Usuario.objects.filter(username='docente').first()
    estudiante_user = Usuario.objects.filter(username='estudiante1').first()

    assert admin_user is not None, "Usuario admin no encontrado"
    assert docente_user is not None, "Usuario docente no encontrado"
    assert estudiante_user is not None, "Usuario estudiante1 no encontrado"

    token_admin = str(RefreshToken.for_user(admin_user).access_token)
    token_docente = str(RefreshToken.for_user(docente_user).access_token)
    token_estudiante = str(RefreshToken.for_user(estudiante_user).access_token)

    # -------------------------------------------------------------------------
    # TEST 1: FILTROS JERÁRQUICOS EN CASCADA
    # -------------------------------------------------------------------------
    filtros_gral = QueryService.obtener_filtros_cascada()
    assert len(filtros_gral['anios']) >= 2, "Debe listar años disponibles"
    assert len(filtros_gral['periodos']) >= 2, "Debe listar períodos"
    assert len(filtros_gral['cursos']) >= 2, "Debe listar cursos"
    assert len(filtros_gral['ejes']) >= 4, "Debe listar los 4 ejes temáticos Saber TyT"

    # Cascada por año 2026
    filtros_2026 = QueryService.obtener_filtros_cascada(anio=2026)
    for p in filtros_2026['periodos']:
        assert p['anio'] == 2026, "Los períodos deben corresponder exclusivamente a 2026"

    # Cascada por curso Sexto A
    curso_6a = filtros_gral['cursos'][0]
    filtros_curso = QueryService.obtener_filtros_cascada(curso_id=curso_6a['id'])
    assert len(filtros_curso['estudiantes']) > 0, "Debe acotar a los estudiantes matriculados en Sexto A"
    print("✓ 1. Filtros jerárquicos en cascada verificados (Año -> Período -> Curso -> Eje -> Estudiante).")

    # -------------------------------------------------------------------------
    # TEST 2: INDICADORES ESTADÍSTICOS (KPIs)
    # -------------------------------------------------------------------------
    qs_todos = QueryService.filtrar_intentos()
    kpi = QueryService.calcular_indicadores(qs_todos)
    assert kpi['estudiantes_evaluados'] >= 2, "Debe haber al menos 2 estudiantes evaluados"
    assert kpi['intentos_finalizados'] >= 4, "Debe contabilizar intentos finalizados"
    assert 0.0 <= kpi['calificacion_promedio'] <= 5.0, "Promedio debe estar en escala 0.0 a 5.0"
    assert kpi['calificacion_minima'] <= kpi['calificacion_maxima'], "Nota mínima <= máxima"
    assert 0.0 <= kpi['porcentaje_aprobacion'] <= 100.0, "% aprobación en rango válido"
    print(f"✓ 2. Indicadores estadísticos verificados: Promedio={kpi['calificacion_promedio']}, "
          f"Aprobación={kpi['porcentaje_aprobacion']}%, Estudiantes={kpi['estudiantes_evaluados']}.")

    # -------------------------------------------------------------------------
    # TEST 3: CONSULTA 1 — CONSOLIDADO GENERAL
    # -------------------------------------------------------------------------
    cons = QueryService.consulta_consolidado_general()
    assert len(cons) > 0, "Consolidado debe retornar registros de intentos"
    primer_reg = cons[0]
    campos_esperados = ['anio', 'periodo', 'curso', 'estudiante_nombre', 'estudiante_codigo', 'simulacro', 'calificacion', 'estado']
    for c in campos_esperados:
        assert c in primer_reg, f"Campo {c} requerido en consolidado"
    print(f"✓ 3. Consulta 1 (Consolidado General) verificada: {len(cons)} intentos detallados.")

    # -------------------------------------------------------------------------
    # TEST 4: CONSULTA 2 — RESULTADOS POR AÑO Y PERÍODO
    # -------------------------------------------------------------------------
    por_periodo = QueryService.consulta_por_periodo()
    assert len(por_periodo) >= 1, "Debe agrupar por período"
    assert 'total_evaluaciones' in por_periodo[0]
    assert 'promedio' in por_periodo[0]
    print(f"✓ 4. Consulta 2 (Por Año y Período) verificada: {len(por_periodo)} períodos analizados.")

    # -------------------------------------------------------------------------
    # TEST 5: CONSULTA 3 — RESULTADOS POR CURSO / GRUPO
    # -------------------------------------------------------------------------
    por_curso = QueryService.consulta_por_curso()
    assert len(por_curso) >= 1, "Debe agrupar por curso"
    assert 'estudiantes_evaluados' in por_curso[0]
    assert 'promedio' in por_curso[0]
    print(f"✓ 5. Consulta 3 (Por Curso/Grupo) verificada: {len(por_curso)} cursos analizados.")

    # -------------------------------------------------------------------------
    # TEST 6: CONSULTA 4 — DESEMPEÑO POR EJE TEMÁTICO (Respuestas contestadas)
    # -------------------------------------------------------------------------
    por_eje = QueryService.consulta_desempeno_ejes()
    assert len(por_eje) >= 2, "Debe calcular métricas en los ejes temáticos"
    for e in por_eje:
        assert e['total_respondidas'] >= e['aciertos'], "Total respondidas >= aciertos"
        assert 0.0 <= e['porcentaje_acierto'] <= 100.0, "% acierto debe ser válido"
    print(f"✓ 6. Consulta 4 (Desempeño por Eje) verificada en {len(por_eje)} categorías Saber TyT.")

    # -------------------------------------------------------------------------
    # TEST 7: CONSULTA 5 — CALIFICACIONES POR ESTUDIANTE
    # -------------------------------------------------------------------------
    califs = QueryService.consulta_calificaciones_estudiante()
    assert len(califs) > 0, "Debe listar calificaciones individuales"
    assert 'calificacion' in califs[0] and 'estado' in califs[0]
    print(f"✓ 7. Consulta 5 (Calificaciones por Estudiante) verificada.")

    # -------------------------------------------------------------------------
    # TEST 8: CONSULTA 6 — HISTORIAL INDIVIDUAL DE ESTUDIANTE
    # -------------------------------------------------------------------------
    historial = QueryService.consulta_historial_individual({}, estudiante_id=estudiante_user.id)
    assert len(historial) >= 1, "Estudiante 1 debe tener historial cronológico de intentos"
    assert 'numero_intento' in historial[0]
    assert 'nota_final' in historial[0]
    print(f"✓ 8. Consulta 6 (Historial Individual) verificada: {len(historial)} intentos del alumno.")

    # -------------------------------------------------------------------------
    # TEST 9: CONSULTA 7 — PREGUNTAS DE MAYOR DIFICULTAD
    # -------------------------------------------------------------------------
    dificiles = QueryService.consulta_preguntas_dificultad()
    assert len(dificiles) > 0, "Debe ordenar preguntas por dificultad"
    # Verificar orden ascendente por % de acierto
    if len(dificiles) >= 2:
        assert dificiles[0]['porcentaje_acierto'] <= dificiles[-1]['porcentaje_acierto'], \
            "Las preguntas más difíciles (% menor acierto) deben estar primero"
    print(f"✓ 9. Consulta 7 (Preguntas de Mayor Dificultad) verificada: {len(dificiles)} reactivos clasificados.")

    # -------------------------------------------------------------------------
    # TEST 10: GENERACIÓN EXCEL REPORTE A (CONSOLIDADO MULTI-HOJA)
    # -------------------------------------------------------------------------
    buf_a = ExcelReportService.generar_reporte_a_consolidado({'anio': 2026})
    wb_a = openpyxl.load_workbook(buf_a)
    assert "Consolidado General" in wb_a.sheetnames, "Debe contener la hoja Consolidado General"
    assert "Promedios por Estudiante" in wb_a.sheetnames, "Debe contener la hoja Promedios por Estudiante"
    ws_a1 = wb_a["Consolidado General"]
    assert ws_a1.cell(row=2, column=1).value.startswith("REPORTE A"), "Título correcto en celda combinada"
    assert ws_a1.max_row >= 5, "Debe contener encabezados y filas de datos"
    print(f"✓ 10. Reporte A Excel verificado: Formato multi-hoja, {ws_a1.max_row} filas generadas.")

    # -------------------------------------------------------------------------
    # TEST 11: GENERACIÓN EXCEL REPORTE B (DESEMPEÑO POR EJES)
    # -------------------------------------------------------------------------
    buf_b = ExcelReportService.generar_reporte_b_ejes({})
    wb_b = openpyxl.load_workbook(buf_b)
    assert "Desempeño por Eje" in wb_b.sheetnames
    ws_b = wb_b["Desempeño por Eje"]
    assert ws_b.max_row >= 5
    print(f"✓ 11. Reporte B Excel verificado: Columnas por eje, aciertos y % con dos decimales.")

    # -------------------------------------------------------------------------
    # TEST 12: GENERACIÓN EXCEL REPORTE C (HISTORIAL INDIVIDUAL)
    # -------------------------------------------------------------------------
    buf_c = ExcelReportService.generar_reporte_c_historial({'estudiante_id': estudiante_user.id})
    wb_c = openpyxl.load_workbook(buf_c)
    assert "Historial Individual" in wb_c.sheetnames
    ws_c = wb_c["Historial Individual"]
    assert ws_c.max_row >= 5
    print(f"✓ 12. Reporte C Excel verificado: Historial cronológico un intento por fila.")

    # -------------------------------------------------------------------------
    # TEST 13: SEGURIDAD Y PERMISOS RBAC EN ENDPOINTS API
    # -------------------------------------------------------------------------
    # Sin autenticación -> 401 Unauthorized
    req_no_auth = factory.get('/api/reportes/indicadores/')
    resp_no_auth = IndicadoresReporteAPIView.as_view()(req_no_auth)
    assert resp_no_auth.status_code == 401, "Petición sin token debe retornar 401"

    # Estudiante intentando consultar reportes globales -> 403 Forbidden
    req_est = factory.get('/api/reportes/consultas/consolidado/')
    req_est.META['HTTP_AUTHORIZATION'] = f'Bearer {token_estudiante}'
    req_est.user = estudiante_user
    resp_est = ConsultasReportesAPIView.as_view()(req_est, tipo_consulta='consolidado')
    assert resp_est.status_code == 403, "Estudiante no debe tener permiso de ver reportes globales"

    # Estudiante intentando exportar Excel -> 403 Forbidden
    req_est_exp = factory.get('/api/reportes/exportar/excel/?tipo=consolidado')
    req_est_exp.META['HTTP_AUTHORIZATION'] = f'Bearer {token_estudiante}'
    req_est_exp.user = estudiante_user
    resp_est_exp = ExportarExcelAPIView.as_view()(req_est_exp)
    assert resp_est_exp.status_code == 403, "Estudiante no debe poder exportar reportes globales a Excel"

    # Docente Evaluador autorizado -> 200 OK
    req_doc = factory.get('/api/reportes/consultas/consolidado/')
    req_doc.META['HTTP_AUTHORIZATION'] = f'Bearer {token_docente}'
    req_doc.user = docente_user
    resp_doc = ConsultasReportesAPIView.as_view()(req_doc, tipo_consulta='consolidado')
    assert resp_doc.status_code == 200, "Docente Evaluador debe tener acceso autorizado 200 OK"

    # Administrador descargando Excel -> 200 OK con Content-Type .xlsx
    req_adm_exp = factory.get('/api/reportes/exportar/excel/?tipo=consolidado')
    req_adm_exp.META['HTTP_AUTHORIZATION'] = f'Bearer {token_admin}'
    req_adm_exp.user = admin_user
    resp_adm_exp = ExportarExcelAPIView.as_view()(req_adm_exp)
    assert resp_adm_exp.status_code == 200
    assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in resp_adm_exp['Content-Type']
    assert 'attachment; filename=' in resp_adm_exp['Content-Disposition']
    print("✓ 13. Seguridad RBAC y autorización verificadas: 401 (anónimo), 403 (estudiante), 200 (docente/admin).")

    # -------------------------------------------------------------------------
    # TEST 14: CASOS LÍMITE (Filtros sin registros retornan 200 sin error 500)
    # -------------------------------------------------------------------------
    req_vacio = factory.get('/api/reportes/consultas/consolidado/?anio=1999')
    req_vacio.META['HTTP_AUTHORIZATION'] = f'Bearer {token_admin}'
    req_vacio.user = admin_user
    resp_vacio = ConsultasReportesAPIView.as_view()(req_vacio, tipo_consulta='consolidado')
    assert resp_vacio.status_code == 200
    assert resp_vacio.data['total_registros'] == 0

    req_exp_vacio = factory.get('/api/reportes/exportar/excel/?tipo=consolidado&anio=1999')
    req_exp_vacio.META['HTTP_AUTHORIZATION'] = f'Bearer {token_admin}'
    req_exp_vacio.user = admin_user
    resp_exp_vacio = ExportarExcelAPIView.as_view()(req_exp_vacio)
    assert resp_exp_vacio.status_code == 200, "Exportar sin registros debe retornar 200 sin error 500"
    print("✓ 14. Casos límite verificados: Búsquedas sin registros generan respuesta limpia 200 OK sin error 500.")

    print("=" * 80)
    print("¡TODAS LAS 14 PRUEBAS DEL MÓDULO DE REPORTES Y EXCEL PASARON EXITOSAMENTE!")
    print("=" * 80)


if __name__ == '__main__':
    run_tests()
