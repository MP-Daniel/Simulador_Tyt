from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Categoria(models.Model):
    """
    Categorías o Competencias evaluadas en las pruebas Saber TyT
    (ej. Razonamiento Cuantitativo, Lectura Crítica, Competencias Ciudadanas, Inglés).
    """
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría / Competencia'
        verbose_name_plural = 'Categorías / Competencias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Pregunta(models.Model):
    """
    Banco de reactivos centralizado.
    Soporta Selección Múltiple con Única Respuesta y Verdadero o Falso.
    """
    TIPO_CHOICES = [
        ('MULTIPLE', 'Selección Múltiple con Única Respuesta'),
        ('VERDADERO_FALSO', 'Verdadero o Falso'),
    ]

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='preguntas',
        help_text="Competencia de la prueba Saber TyT"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='MULTIPLE')
    texto_base = models.TextField(blank=True, null=True, help_text="Contexto previo, caso o lectura introductoria")
    enunciado = models.TextField(help_text="Enunciado de la pregunta")
    retroalimentacion = models.TextField(blank=True, help_text="Justificación didáctica de la respuesta correcta")
    puntaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('2.50'),
        help_text="Puntaje base mayor que cero (R02)"
    )
    activo = models.BooleanField(default=True, help_text="Permite activar o desactivar reactivos sin eliminarlos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'preguntas'
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['categoria', 'id']

    def __str__(self):
        enunciado_corto = self.enunciado[:60] + ('...' if len(self.enunciado) > 60 else '')
        return f"[{self.categoria.nombre}] ({self.tipo}) {enunciado_corto}"

    def clean(self):
        # Regla R02: El puntaje base debe ser mayor que cero
        if self.puntaje is not None and self.puntaje <= Decimal('0.00'):
            raise ValidationError({'puntaje': 'El puntaje debe ser estrictamente mayor que cero.'})

    @property
    def opcion_correcta(self):
        """Retorna la opción correcta de la pregunta si existe."""
        return self.opciones.filter(es_correcta=True).first()


class OpcionRespuesta(models.Model):
    """
    Alternativas de respuesta asociadas a cada pregunta.
    Reglas:
    - R05: Cada pregunta debe tener una sola respuesta correcta.
    - R06: Las preguntas de verdadero o falso solo tendrán dos opciones ('V' y 'F').
    """
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='opciones'
    )
    letra = models.CharField(max_length=5, help_text="Letra identificadora (A, B, C, D o V, F)")
    texto = models.TextField()
    es_correcta = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'opciones_respuesta'
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'
        ordering = ['pregunta', 'orden', 'letra']
        unique_together = [['pregunta', 'letra']]

    def __str__(self):
        correcta_str = "✓ Correcta" if self.es_correcta else ""
        return f"{self.pregunta_id} - {self.letra}) {self.texto[:40]} {correcta_str}"


class Importacion(models.Model):
    """
    Registro histórico de importaciones desde Excel para trazabilidad y auditoría.
    Almacena totales de filas leídas, válidas, duplicadas y reporte de errores (R10).
    """
    archivo_nombre = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    total_filas = models.IntegerField(default=0)
    filas_validas = models.IntegerField(default=0)
    filas_duplicadas = models.IntegerField(default=0)
    filas_error = models.IntegerField(default=0)
    detalles_errores = models.JSONField(default=list, blank=True)
    usuario = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'importaciones'
        verbose_name = 'Importación de Preguntas'
        verbose_name_plural = 'Importaciones de Preguntas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Importación {self.archivo_nombre} ({self.fecha.strftime('%d/%m/%Y %H:%M')}) - Válidas: {self.filas_validas}"
