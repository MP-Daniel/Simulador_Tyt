from django.contrib import admin
from .models import Categoria, Pregunta, OpcionRespuesta, Importacion

class OpcionRespuestaInline(admin.TabularInline):
    model = OpcionRespuesta
    extra = 4

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'created_at')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activo',)

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'tipo', 'enunciado_corto', 'puntaje', 'activo', 'created_at')
    search_fields = ('enunciado', 'texto_base', 'retroalimentacion')
    list_filter = ('categoria', 'tipo', 'activo')
    inlines = [OpcionRespuestaInline]

    def enunciado_corto(self, obj):
        return obj.enunciado[:60]
    enunciado_corto.short_description = 'Enunciado'

@admin.register(Importacion)
class ImportacionAdmin(admin.ModelAdmin):
    list_display = ('archivo_nombre', 'fecha', 'total_filas', 'filas_validas', 'filas_error', 'usuario')
    readonly_fields = ('fecha', 'detalles_errores')
