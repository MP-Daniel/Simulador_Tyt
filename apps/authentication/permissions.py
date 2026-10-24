from rest_framework import permissions


class HasCustomPermission(permissions.BasePermission):
    """
    Verifica que el usuario autenticado tenga el permiso granular requerido.
    Se define en la vista mediante: required_permission = 'codigo.del.permiso'.
    Garantiza que la restricción se aplique en Django y no solo en la UI (Sec 2.1).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not request.user.is_active:
            return False

        if request.user.is_superuser:
            return True

        required_perm = getattr(view, 'required_permission', None)
        if not required_perm:
            return True

        return request.user.tiene_permiso(required_perm)


class IsAdminRole(permissions.BasePermission):
    """Permite el acceso exclusivamente a usuarios con rol de Administrador o superusuarios."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_active and request.user.es_administrador


class IsStudentRole(permissions.BasePermission):
    """Permite el acceso a usuarios con rol de Estudiante."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_active and request.user.es_estudiante


def require_permission(perm_code):
    """
    Generador de clases de permiso dinámicas para vistas basadas en clase.
    Ejemplo: permission_classes = [IsAuthenticated, require_permission('usuarios.administrar')]
    """
    class SpecificPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            if not request.user or not request.user.is_authenticated:
                return False
            if not request.user.is_active:
                return False
            return request.user.tiene_permiso(perm_code)
    return SpecificPermission
