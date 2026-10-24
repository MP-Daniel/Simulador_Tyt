from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Cuestionario(models.Model):
    """
    Parametrización y configuración de los simulacros Saber TyT (Sec 2.4).
    Aplica las reglas de negocio R01, R02, R03, R04 y R08.
    """
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('programado', 'Programado'),
        ('disponible', 'Disponible'),
        ('cerrado', 'Cerrado'),
    ]

    nombre = models.CharField(max_length=200, help_text="Título o nombre del simulacro")
    descripcion = models.TextField(blank=True, help_text="Instrucciones y objetivos del examen")
    fecha_apertura = models.DateTimeField(help_text="Fecha y hora en que se habilita la presentación (R01)")
    fecha_cierre = models.DateTimeField(help_text="Fecha y hora límite de presentación (R01)")
    tiempo_limite_minutos = models.PositiveIntegerField(
        default=60,
        help_text="Minutos otorgados al participante para responder (R04 > 0)"
    )
    intentos_permitidos = models.PositiveIntegerField(
        default=2,
        help_text="Número máximo de intentos permitidos por estudiante (R04 > 0)"
    )
    calificacion_maxima = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Escala máxima de calificación (R02 > 0, ej. 5.00)"
    )
    calificacion_aprobacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('3.00'),
        help_text="Nota mínima requerida para aprobar (R03 <= máxima)"
    )
    mezclar_preguntas = models.BooleanField(
        default=True,
        help_text="Barajar el orden de los reactivos en cada intento"
    )
    mezclar_respuestas = models.BooleanField(
        default=True,
        help_text="Barajar las alternativas A, B, C, D de cada pregunta"
    )
    permitir_revision = models.BooleanField(
        default=True,
        help_text="Permitir ver respuestas correctas y justificación formativa al finalizar"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='borrador',
        help_text="Estado del ciclo de vida del cuestionario"
    )
    activo = models.BooleanField(default=True, help_text="Permite activar o desactivar cuestionarios")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relación N:M con Banco de Preguntas (Regla R07)
    preguntas = models.ManyToManyField(
        'banco_preguntas.Pregunta',
        through='CuestionarioPregunta',
        related_name='cuestionarios',
        blank=True
    )

    class Meta:
        db_table = 'cuestionarios'
        verbose_name = 'Cuestionario'
        verbose_name_plural = 'Cuestionarios'
        ordering = ['-fecha_apertura', 'nombre']

    def __str__(self):
        return f"{self.nombre} [{self.estado.upper()}] ({self.cuestionario_preguntas.count()} preguntas)"

    def clean(self):
        # Regla R01: La fecha de cierre debe ser posterior a la fecha de apertura
        if self.fecha_apertura and self.fecha_cierre:
            if self.fecha_cierre <= self.fecha_apertura:
                raise ValidationError({
                    'fecha_cierre': 'Regla R01 violada: La fecha de cierre debe ser estrictamente posterior a la fecha de apertura.'
                })

        # Regla R02: La calificación máxima debe ser mayor que cero
        if self.calificacion_maxima is not None and self.calificacion_maxima <= Decimal('0.00'):
            raise ValidationError({
                'calificacion_maxima': 'Regla R02 violada: La calificación máxima debe ser mayor que cero.'
            })

        # Regla R03: La nota para aprobar debe estar entre cero y la calificación máxima
        if self.calificacion_aprobacion is not None and self.calificacion_maxima is not None:
            if self.calificacion_aprobacion < Decimal('0.00') or self.calificacion_aprobacion > self.calificacion_maxima:
                raise ValidationError({
                    'calificacion_aprobacion': 'Regla R03 violada: La nota de aprobación debe estar entre 0.00 y la calificación máxima.'
                })

        # Regla R04: Tiempo límite e intentos deben ser mayores que cero
        if self.tiempo_limite_minutos is not None and self.tiempo_limite_minutos <= 0:
            raise ValidationError({'tiempo_limite_minutos': 'Regla R04 violada: El tiempo límite debe ser mayor que cero.'})
        if self.intentos_permitidos is not None and self.intentos_permitidos <= 0:
            raise ValidationError({'intentos_permitidos': 'Regla R04 violada: Los intentos permitidos deben ser mayores que cero.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def esta_disponible_ahora(self):
        """
        Validación del lado del servidor para verificar si un cuestionario está disponible (Regla R08 y Sec 2.4).
        """
        if not self.activo:
            return False, "El cuestionario se encuentra desactivado."
        if self.estado != 'disponible':
            return False, f"El cuestionario se encuentra en estado '{self.get_estado_display()}'."

        ahora = timezone.now()
        if ahora < self.fecha_apertura:
            return False, f"El cuestionario aún no ha abierto. Apertura programada para: {self.fecha_apertura.strftime('%d/%m/%Y %H:%M')}."
        if ahora > self.fecha_cierre:
            return False, f"El cuestionario ha cerrado. La fecha límite fue: {self.fecha_cierre.strftime('%d/%m/%Y %H:%M')}."

        if self.cuestionario_preguntas.count() == 0:
            return False, "El cuestionario no tiene preguntas asignadas todavía."

        return True, "Cuestionario disponible para presentar."

    def puede_iniciar_estudiante(self, usuario):
        """
        Verifica desde el servidor si el estudiante puede iniciar un nuevo intento (Sec 2.4 y R08).
        """
        disponible, motivo = self.esta_disponible_ahora()
        if not disponible:
            return False, motivo

        from evaluaciones.models import Intento
        intentos_realizados = Intento.objects.filter(
            cuestionario=self,
            estudiante=usuario,
            estado_intento__in=['finalizado', 'en_progreso']
        ).count()

        if intentos_realizados >= self.intentos_permitidos:
            return False, f"Has alcanzado el límite de intentos permitidos ({self.intentos_permitidos}/{self.intentos_permitidos})."

        return True, "Habilitado para presentar."

    @property
    def puntaje_total_posible(self):
        """Suma de los puntajes de las preguntas que componen el cuestionario."""
        total = self.cuestionario_preguntas.aggregate(models.Sum('puntaje'))['puntaje__sum']
        return total or Decimal('0.00')


class CuestionarioPregunta(models.Model):
    """
    Tabla intermedia que relaciona preguntas con cuestionarios ($N:M$ - Regla R07).
    Permite definir un puntaje y orden personalizado por reactivo dentro de cada examen.
    """
    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='cuestionario_preguntas'
    )
    pregunta = models.ForeignKey(
        'banco_preguntas.Pregunta',
        on_delete=models.CASCADE,
        related_name='pregunta_cuestionarios'
    )
    puntaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Puntaje otorgado a esta pregunta dentro del cuestionario"
    )
    orden = models.PositiveIntegerField(default=1, help_text="Posición de visualización")

    class Meta:
        db_table = 'cuestionario_preguntas'
        verbose_name = 'Pregunta de Cuestionario'
        verbose_name_plural = 'Preguntas de Cuestionario'
        ordering = ['cuestionario', 'orden', 'id']
        unique_together = [['cuestionario', 'pregunta']]

    def __str__(self):
        return f"{self.cuestionario.nombre} -> P#{self.pregunta_id} ({self.puntaje} pts)"
