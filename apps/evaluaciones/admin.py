from django.contrib import admin
from .models import Intento, RespuestaIntento, PeriodoAcademico, Curso, Matricula

@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'anio', 'nombre', 'activo', 'created_at')
    list_filter = ('anio', 'activo')
    search_fields = ('nombre',)

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo', 'periodo', 'programa', 'activo')
    list_filter = ('periodo__anio', 'periodo', 'activo')
    search_fields = ('nombre', 'codigo')

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'curso', 'fecha_matricula')
    list_filter = ('curso__periodo__anio', 'curso__periodo', 'curso')
    search_fields = ('estudiante__username', 'estudiante__codigo_estudiantil', 'curso__nombre')

class RespuestaIntentoInline(admin.TabularInline):
    model = RespuestaIntento
    extra = 0
    readonly_fields = ('pregunta', 'opcion_seleccionada', 'es_acierto', 'puntaje_obtenido', 'marcada_revision', 'respondida_en')

@admin.register(Intento)
class IntentoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'estudiante', 'curso', 'cuestionario', 'numero_intento',
        'calificacion', 'resultado', 'estado_intento',
        'aciertos', 'errores', 'omitidas', 'fecha_inicio'
    )
    list_filter = ('resultado', 'estado_intento', 'curso', 'cuestionario')
    search_fields = ('estudiante__username', 'estudiante__codigo_estudiantil', 'cuestionario__nombre')
    inlines = [RespuestaIntentoInline]
