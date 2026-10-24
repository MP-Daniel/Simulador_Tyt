from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CuestionarioViewSet

router = DefaultRouter()
router.register(r'cuestionarios', CuestionarioViewSet, basename='cuestionarios')

urlpatterns = [
    path('disponibles/', CuestionarioViewSet.as_view({'get': 'disponibles'}), name='cuestionarios_disponibles_direct'),
    path('<int:pk>/previsualizar/', CuestionarioViewSet.as_view({'get': 'previsualizar'}), name='cuestionarios_previsualizar_direct'),
    path('', include(router.urls)),
]
