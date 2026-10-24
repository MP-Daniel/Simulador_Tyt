from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet,
    PreguntaViewSet,
    ImportarExcelView,
    DescargarPlantillaExcelView
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'preguntas', PreguntaViewSet, basename='preguntas')

urlpatterns = [
    path('importar-excel/', ImportarExcelView.as_view(), name='importar_excel'),
    path('descargar-plantilla/', DescargarPlantillaExcelView.as_view(), name='descargar_plantilla'),
    path('', include(router.urls)),
]
