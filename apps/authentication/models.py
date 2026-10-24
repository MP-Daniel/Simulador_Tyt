from django.db import models
from django.contrib.auth.models import AbstractUser


class Permiso(models.Model):
    """
    Permisos granulares del sistema.
    Permite habilitar o restringir individualmente las funcionalidades
    del sistema según las responsabilidades asignadas (Guía Segundo Parcial, Sec 2.2).
    """
    codigo = models.CharField(max_length=100, unique=True, help_text="Código único del permiso (ej. preguntas.gestionar)")
    nombre = models.CharField(max_length=150, help_text="Nombre legible del permiso")
    modulo = models.CharField(max_length=100, help_text="Módulo al que pertenece (ej. Usuarios, Banco, Cuestionarios)")
    descripcion = models.TextField(blank=True, help_text="Explicación del alcance de este permiso")

    class Meta:
        db_table = 'permisos'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['modulo', 'codigo']

    def __str__(self):
        return f"{self.modulo} • {self.nombre} ({self.codigo})"


class Rol(models.Model):
    """
    Roles del sistema con permisos configurables.
    Roles predeterminados: Administrador y Estudiante.
    Permite además crear, editar, activar y desactivar roles personalizados
    (ej. Docente Evaluador) con permisos atómicos asignables.
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del rol (ej. Administrador, Estudiante, Docente Evaluador)")
    descripcion = models.TextField(blank=True, help_text="Descripción de las funciones asignadas a este rol")
    es_predeterminado = models.BooleanField(default=False, help_text="Indica si es un rol base del sistema (Administrador / Estudiante)")
    activo = models.BooleanField(default=True, help_text="Controla si los usuarios con este rol pueden operar")
    permisos = models.ManyToManyField(Permiso, related_name='roles', blank=True, help_text="Permisos habilitados para este rol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} ({estado})"

    def tiene_permiso(self, codigo_permiso):
        """Verifica si el rol tiene asignado un permiso específico y está activo."""
        if not self.activo:
            return False
        return self.permisos.filter(codigo=codigo_permiso).exists()


class Usuario(AbstractUser):
    """
    Usuario del Simulador Saber TyT.
    Soporta autenticación con nombre de usuario y contraseña, generación
    de tokens JWT, desactivación de cuenta y autorización por rol.
    """
    codigo_estudiantil = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Código estudiantil o documento de identidad"
    )
    programa_academico = models.CharField(
        max_length=150,
        blank=True,
        default='Ingeniería de Sistemas',
        help_text="Programa académico del usuario"
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        help_text="Rol asignado al usuario"
    )
    telefono = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        rol_nombre = self.rol.nombre if self.rol else "Sin rol"
        return f"{self.username} - {self.get_full_name() or self.username} ({rol_nombre})"

    def tiene_permiso(self, codigo_permiso):
        """
        Verificación estricta en Django (no solo interfaz, según Guía Sec 2.1).
        Superusuarios tienen todos los permisos. Si no, se evalúa el rol del usuario.
        """
        if self.is_superuser:
            return True
        if not self.is_active:
            return False
        if not self.rol or not self.rol.activo:
            return False
        return self.rol.tiene_permiso(codigo_permiso)

    @property
    def es_administrador(self):
        """Identifica si es Administrador del sistema."""
        return self.is_superuser or (self.rol and self.rol.nombre == 'Administrador')

    @property
    def es_estudiante(self):
        """Identifica si es Estudiante."""
        return self.rol and self.rol.nombre == 'Estudiante'
