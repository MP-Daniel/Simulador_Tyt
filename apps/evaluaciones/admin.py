from django.contrib import admin
from .models import Intento, RespuestaIntento

class RespuestaIntentoInline(admin.TabularInline):
    model = RespuestaIntento
    extra = 0
    readonly_fields = ('pregunta', 'opcion_seleccionada', 'es_acierto', 'puntaje_obtenido', 'marcada_revision', 'respondida_en')

@admin.register(Intento)
class IntentoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'estudiante', 'cuestionario', 'numero_intento',
        'calificacion', 'resultado', 'estado_intento',
        'aciertos', 'errores', 'omitidas', 'fecha_inicio'
    )
    list_filter = ('resultado', 'estado_intento', 'cuestionario')
    search_fields = ('estudiante__username', 'estudiante__codigo_estudiantil', 'cuestionario__nombre')
    inlines = [RespuestaIntentoInline]
