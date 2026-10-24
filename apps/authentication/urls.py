from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomLoginView,
    MeView,
    LogoutView,
    PermisoListView,
    RolViewSet,
    UsuarioViewSet
)

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='roles')
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    # Autenticación JWT (Sec 2.1)
    path('login/', CustomLoginView.as_view(), name='jwt_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('me/', MeView.as_view(), name='jwt_me'),
    path('logout/', LogoutView.as_view(), name='jwt_logout'),

    # Permisos granulares
    path('permisos/', PermisoListView.as_view(), name='permisos_list'),

    # Router de Usuarios y Roles
    path('', include(router.urls)),
]
