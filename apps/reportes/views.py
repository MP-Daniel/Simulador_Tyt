"""
Vistas API REST para el Módulo de Consultas, Indicadores y Exportación a Excel.
Protegidas mediante JWT y permiso atómico 'resultados.consultar_todos'.
"""
from datetime import datetime
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authentication.permissions import require_permission
from reportes.services.query_service import QueryService
from reportes.services.excel_service import ExcelReportService


def _extraer_filtros_request(request):
    """Auxiliar para parsear parámetros de consulta desde la URL."""
    p = request.query_params
    filtros = {}
    if p.get('anio'):
        try:
            filtros['anio'] = int(p.get('anio'))
        except (ValueError, TypeError):
            pass

    if p.get('periodo_id'):
        try:
            filtros['periodo_id'] = int(p.get('periodo_id'))
        except (ValueError, TypeError):
            pass

    if p.get('curso_id'):
        try:
            filtros['curso_id'] = int(p.get('curso_id'))
        except (ValueError, TypeError):
            pass

    if p.get('categoria_id'):
        try:
            filtros['categoria_id'] = int(p.get('categoria_id'))
        except (ValueError, TypeError):
            pass

    if p.get('estudiante_id'):
        try:
            filtros['estudiante_id'] = int(p.get('estudiante_id'))
        except (ValueError, TypeError):
            pass

    if p.get('busqueda'):
        filtros['busqueda'] = p.get('busqueda').strip()

    if p.get('orden'):
        filtros['orden'] = p.get('orden').strip()

    # Nombres descriptivos para metadatos del reporte Excel
    if p.get('periodo_nombre'):
        filtros['periodo_nombre'] = p.get('periodo_nombre').strip()
    if p.get('curso_nombre'):
        filtros['curso_nombre'] = p.get('curso_nombre').strip()
    if p.get('eje_nombre'):
        filtros['eje_nombre'] = p.get('eje_nombre').strip()

    return filtros


class FiltrosCascadaAPIView(APIView):
    """
    Retorna las opciones de filtros jerárquicos según la selección actual:
    AÑO -> PERÍODO -> CURSO -> EJE TEMÁTICO -> ESTUDIANTE.
    """
    permission_classes = [IsAuthenticated, require_permission('resultados.consultar_todos')]

    def get(self, request):
        anio = request.query_params.get('anio')
        periodo_id = request.query_params.get('periodo_id')
        curso_id = request.query_params.get('curso_id')

        anio_int = int(anio) if anio and anio.isdigit() else None
        periodo_int = int(periodo_id) if periodo_id and periodo_id.isdigit() else None
        curso_int = int(curso_id) if curso_id and curso_id.isdigit() else None

        data = QueryService.obtener_filtros_cascada(
            anio=anio_int,
            periodo_id=periodo_int,
            curso_id=curso_int
        )
        return Response(data, status=status.HTTP_200_OK)


class IndicadoresReporteAPIView(APIView):
    """
    Calcula los 6 indicadores estadísticos clave aplicando los filtros seleccionados.
    """
    permission_classes = [IsAuthenticated, require_permission('resultados.consultar_todos')]

    def get(self, request):
        filtros = _extraer_filtros_request(request)
        qs = QueryService.filtrar_intentos(filtros)
        indicadores = QueryService.calcular_indicadores(qs)
        return Response(indicadores, status=status.HTTP_200_OK)


class ConsultasReportesAPIView(APIView):
    """
    Expone las 7 consultas obligatorias con paginación configurable (por defecto 10 registros).
    Tipos soportados:
    - 'consolidado'
    - 'periodo'
    - 'curso'
    - 'ejes'
    - 'calificaciones'
    - 'historial'
    - 'dificultad'
    """
    permission_classes = [IsAuthenticated, require_permission('resultados.consultar_todos')]

    def get(self, request, tipo_consulta):
        filtros = _extraer_filtros_request(request)

        # Mapeo a métodos de servicio
        mapa_consultas = {
            'consolidado': QueryService.consulta_consolidado_general,
            'periodo': QueryService.consulta_por_periodo,
            'curso': QueryService.consulta_por_curso,
            'ejes': QueryService.consulta_desempeno_ejes,
            'calificaciones': QueryService.consulta_calificaciones_estudiante,
            'historial': lambda f: QueryService.consulta_historial_individual(f, f.get('estudiante_id')),
            'dificultad': QueryService.consulta_preguntas_dificultad,
        }

        if tipo_consulta not in mapa_consultas:
            return Response({
                'detail': f"Tipo de consulta '{tipo_consulta}' no válido. Opciones: {list(mapa_consultas.keys())}"
            }, status=status.HTTP_400_BAD_REQUEST)

        registros = mapa_consultas[tipo_consulta](filtros)

        # Paginación
        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1

        try:
            page_size = max(1, min(100, int(request.query_params.get('page_size', 10))))
        except (ValueError, TypeError):
            page_size = 10

        total_items = len(registros)
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        page = min(page, total_pages)

        start = (page - 1) * page_size
        end = start + page_size
        data_pagina = registros[start:end]

        return Response({
            'tipo_consulta': tipo_consulta,
            'pagina_actual': page,
            'tamano_pagina': page_size,
            'total_registros': total_items,
            'total_paginas': total_pages,
            'registros': data_pagina
        }, status=status.HTTP_200_OK)


class ExportarExcelAPIView(APIView):
    """
    Exporta a Excel (.xlsx) la consulta completa filtrada en base de datos.
    Soporta:
    - 'tipo=consolidado': Reporte A (Consolidado general + hoja de promedios)
    - 'tipo=ejes': Reporte B (Desempeño por eje temático)
    - 'tipo=historial': Reporte C (Historial individual)
    """
    permission_classes = [IsAuthenticated, require_permission('resultados.consultar_todos')]

    def get(self, request):
        tipo_reporte = request.query_params.get('tipo', 'consolidado').lower()
        filtros = _extraer_filtros_request(request)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if tipo_reporte == 'consolidado':
            buffer = ExcelReportService.generar_reporte_a_consolidado(filtros)
            filename = f"ReporteA_Consolidado_SaberTyT_{timestamp}.xlsx"
        elif tipo_reporte in ('ejes', 'eje_tematico'):
            buffer = ExcelReportService.generar_reporte_b_ejes(filtros)
            filename = f"ReporteB_DesempenoEjes_SaberTyT_{timestamp}.xlsx"
        elif tipo_reporte == 'historial':
            buffer = ExcelReportService.generar_reporte_c_historial(filtros)
            filename = f"ReporteC_HistorialIndividual_SaberTyT_{timestamp}.xlsx"
        else:
            return Response({
                'detail': f"Tipo de reporte '{tipo_reporte}' no soportado. Elija 'consolidado', 'ejes' o 'historial'."
            }, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response
