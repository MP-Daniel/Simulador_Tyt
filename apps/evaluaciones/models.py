from django.db import models
from decimal import Decimal


class PeriodoAcademico(models.Model):
    """
    Período académico semestral o anual (ej. 2026-1, 2026-2).
    Sustenta el primer y segundo nivel de filtros jerárquicos de reportes.
    """
    anio = models.PositiveIntegerField(help_text="Año lectivo, ej. 2025, 2026")
    nombre = models.CharField(max_length=20, help_text="Código del período, ej. 2026-1")
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'periodos_academicos'
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'
        ordering = ['-anio', 'nombre']
        unique_together = [['anio', 'nombre']]

    def __str__(self):
        return f"{self.nombre} ({self.anio})"


class Curso(models.Model):
    """
    Curso o grupo académico asociado a un período (ej. Sexto A, Sexto B).
    Sustenta el tercer nivel de filtros jerárquicos de reportes.
    """
    nombre = models.CharField(max_length=100, help_text="Nombre del grupo, ej. Sexto A")
    codigo = models.CharField(max_length=50, blank=True, help_text="Código del curso, ej. SIS-6A")
    periodo = models.ForeignKey(
        PeriodoAcademico,
        on_delete=models.CASCADE,
        related_name='cursos',
        help_text="Período académico al que pertenece el curso"
    )
    programa = models.CharField(max_length=150, default='Ingeniería de Sistemas')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'cursos'
        verbose_name = 'Curso / Grupo'
        verbose_name_plural = 'Cursos / Grupos'
        ordering = ['periodo', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.periodo.nombre}"


class Matricula(models.Model):
    """
    Pertenencia o matrícula de un estudiante a un curso o grupo académico.
    Sustenta el quinto nivel de filtros jerárquicos de reportes (estudiantes del curso).
    """
    estudiante = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    fecha_matricula = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'matriculas'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = [['estudiante', 'curso']]

    def __str__(self):
        return f"{self.estudiante.username} matriculado en {self.curso.nombre}"


class Intento(models.Model):
    """
    Registro inmutable de un intento de presentación de cuestionario (Sec 2.5).
    Conserva estudiante, cuestionario, curso, fechas, tiempos, puntajes y calificación final en DECIMAL(5,2).
    """
    ESTADO_INTENTO_CHOICES = [
        ('en_progreso', 'En progreso'),
        ('finalizado', 'Finalizado'),
        ('anulado', 'Anulado'),
    ]

    ESTADO_CALIFICACION_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('reprobado', 'Reprobado'),
    ]

    cuestionario = models.ForeignKey(
        'cuestionarios.Cuestionario',
        on_delete=models.CASCADE,
        related_name='intentos'
    )
    estudiante = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.CASCADE,
        related_name='intentos'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='intentos',
        help_text="Curso o grupo en el cual se presentó el simulacro"
    )
    numero_intento = models.PositiveIntegerField(default=1)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    duracion_segundos = models.PositiveIntegerField(default=0)

    # Puntajes y calificación con precisión decimal estricta
    puntaje_obtenido = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'))
    puntaje_total_posible = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('0.00'))
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    estado_intento = models.CharField(max_length=20, choices=ESTADO_INTENTO_CHOICES, default='en_progreso')
    resultado = models.CharField(max_length=20, choices=ESTADO_CALIFICACION_CHOICES, default='pendiente')

    # Contadores estadísticos
    total_preguntas = models.PositiveIntegerField(default=0)
    aciertos = models.PositiveIntegerField(default=0)
    errores = models.PositiveIntegerField(default=0)
    omitidas = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'intentos'
        verbose_name = 'Intento de Evaluación'
        verbose_name_plural = 'Intentos de Evaluación'
        ordering = ['-fecha_inicio']

    def __str__(self):
        estudiante_str = self.estudiante.get_full_name() or self.estudiante.username
        return f"Intento #{self.numero_intento} de {estudiante_str} en '{self.cuestionario.nombre}' - Nota: {self.calificacion}"


class RespuestaIntento(models.Model):
    """
    Registro de cada respuesta individual dentro de un intento (Regla R09).
    Conserva tanto las preguntas respondidas como las omitidas (con opcion=NULL).
    """
    intento = models.ForeignKey(
        Intento,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    pregunta = models.ForeignKey(
        'banco_preguntas.Pregunta',
        on_delete=models.CASCADE,
        related_name='respuestas_evaluaciones'
    )
    opcion_seleccionada = models.ForeignKey(
        'banco_preguntas.OpcionRespuesta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selecciones_estudiante'
    )
    es_acierto = models.BooleanField(default=False)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    marcada_revision = models.BooleanField(default=False, help_text="Bandera puesta por el estudiante durante el examen")
    respondida_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'respuestas_intento'
        verbose_name = 'Respuesta de Intento'
        verbose_name_plural = 'Respuestas de Intento'
        ordering = ['intento', 'id']
        unique_together = [['intento', 'pregunta']]

    def __str__(self):
        opcion_str = self.opcion_seleccionada.letra if self.opcion_seleccionada else 'Omitida'
        return f"Intento #{self.intento_id} - Pregunta #{self.pregunta_id}: [{opcion_str}] ({self.puntaje_obtenido} pts)"
