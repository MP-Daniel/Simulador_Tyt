from django.urls import path
from reportes.views import (
    FiltrosCascadaAPIView,
    IndicadoresReporteAPIView,
    ConsultasReportesAPIView,
    ExportarExcelAPIView
)

urlpatterns = [
    path('filtros/', FiltrosCascadaAPIView.as_view(), name='api_reportes_filtros'),
    path('indicadores/', IndicadoresReporteAPIView.as_view(), name='api_reportes_indicadores'),
    path('consultas/<str:tipo_consulta>/', ConsultasReportesAPIView.as_view(), name='api_reportes_consultas'),
    path('exportar/excel/', ExportarExcelAPIView.as_view(), name='api_reportes_exportar_excel'),
]
