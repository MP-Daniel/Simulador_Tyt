from django.contrib import admin
from .models import Cuestionario, CuestionarioPregunta

class CuestionarioPreguntaInline(admin.TabularInline):
    model = CuestionarioPregunta
    extra = 1

@admin.register(Cuestionario)
class CuestionarioAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'estado', 'fecha_apertura', 'fecha_cierre',
        'tiempo_limite_minutos', 'intentos_permitidos',
        'calificacion_maxima', 'calificacion_aprobacion', 'activo'
    )
    list_filter = ('estado', 'activo', 'permitir_revision')
    search_fields = ('nombre', 'descripcion')
    inlines = [CuestionarioPreguntaInline]
