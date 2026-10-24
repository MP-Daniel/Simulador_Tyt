from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .models import Rol, Permiso
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioSerializer,
    RolSerializer,
    PermisoSerializer
)
from .permissions import HasCustomPermission, require_permission, IsAdminRole

Usuario = get_user_model()


class CustomLoginView(TokenObtainPairView):
    """
    Endpoint de Autenticación con JWT (Sec 2.1).
    Valida credenciales (username/password), comprueba que la cuenta esté activa
    y retorna tokens access y refresh con la información del usuario y sus permisos.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    Retorna la información del usuario actualmente autenticado mediante su token JWT,
    incluyendo su rol, estado activo y lista de permisos.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UsuarioSerializer(user)
        permisos_list = []
        if user.is_superuser:
            permisos_list = list(Permiso.objects.values_list('codigo', flat=True))
        elif user.rol and user.rol.activo:
            permisos_list = list(user.rol.permisos.values_list('codigo', flat=True))

        return Response({
            **serializer.data,
            'is_superuser': user.is_superuser,
            'permisos': permisos_list,
            'rol_nombre': user.rol.nombre if (user.rol and user.rol.activo) else ('Administrador' if user.is_superuser else 'Sin rol')
        })


class LogoutView(APIView):
    """
    Cierre de sesión seguro y confirmación de desconexión (Sec 2.1).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # El cliente descarta el token; se puede extender a blacklist de SimpleJWT si se requiere
        return Response({
            'detail': 'Sesión cerrada exitosamente.'
        }, status=status.HTTP_200_OK)


class PermisoListView(APIView):
    """
    Lista todos los permisos granulares disponibles en el sistema.
    Utilizado por el Administrador para configurar roles personalizados.
    """
    permission_classes = [IsAuthenticated, require_permission('roles.administrar')]

    def get(self, request):
        permisos = Permiso.objects.all().order_by('modulo', 'codigo')
        serializer = PermisoSerializer(permisos, many=True)
        return Response(serializer.data)


class RolViewSet(viewsets.ModelViewSet):
    """
    Gestión integral de Roles y Permisos Configurables (Sec 2.2).
    Permite al Administrador:
    - Crear, consultar, editar y activar/desactivar roles.
    - Asignar permisos específicos (ej. crear el rol "Docente Evaluador" con permisos
      para crear preguntas y cuestionarios, sin permitir administrar usuarios).
    """
    queryset = Rol.objects.all().order_by('-es_predeterminado', 'nombre')
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, require_permission('roles.administrar')]

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        rol = self.get_object()
        if rol.es_predeterminado and rol.nombre == 'Administrador':
            return Response(
                {'detail': 'El rol predeterminado Administrador no puede ser desactivado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        rol.activo = not rol.activo
        rol.save()
        return Response({
            'detail': f"Rol '{rol.nombre}' {'activado' if rol.activo else 'desactivado'} correctamente.",
            'activo': rol.activo
        })


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Administración de Usuarios y Cuentas (Sec 2.1 y 2.2).
    Permite al Administrador:
    - Registrar usuarios estudiantes, docentes o administrativos.
    - Asignar roles.
    - Activar y desactivar cuentas (control de acceso verificado en Django).
    """
    queryset = Usuario.objects.all().order_by('-date_joined')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, require_permission('usuarios.administrar')]

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        usuario = self.get_object()
        if usuario == request.user:
            return Response(
                {'detail': 'No puedes desactivar tu propia cuenta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        usuario.is_active = not usuario.is_active
        usuario.save()
        return Response({
            'detail': f"Cuenta de '{usuario.username}' {'activada' if usuario.is_active else 'desactivada'} correctamente.",
            'is_active': usuario.is_active
        })
