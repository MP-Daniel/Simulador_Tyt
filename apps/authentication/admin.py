from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, Permiso

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'modulo')
    search_fields = ('codigo', 'nombre', 'modulo')
    list_filter = ('modulo',)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_predeterminado', 'activo', 'created_at')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('es_predeterminado', 'activo')
    filter_horizontal = ('permisos',)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'codigo_estudiantil', 'email', 'first_name', 'last_name', 'rol', 'is_active')
    search_fields = ('username', 'codigo_estudiantil', 'email', 'first_name', 'last_name')
    list_filter = ('rol', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Saber TyT', {'fields': ('codigo_estudiantil', 'programa_academico', 'rol', 'telefono')}),
    )
