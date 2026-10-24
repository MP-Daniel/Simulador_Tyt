from rest_framework import serializers
from .models import Intento, RespuestaIntento
from banco_preguntas.models import OpcionRespuesta


class OpcionExamenSeguraSerializer(serializers.ModelSerializer):
    """
    Serializer de opciones para la pantalla del examen.
    SEGURIDAD CRÍTICA (Sec 2.5):
    Oculta estrictamente 'es_correcta' para impedir que el estudiante
    inspeccione la respuesta correcta en la consola del navegador.
    """
    class Meta:
        model = OpcionRespuesta
        fields = ['id', 'letra', 'texto', 'orden']


class PreguntaExamenSeguraSerializer(serializers.Serializer):
    """
    Serializer seguro para la presentación del examen.
    NO expone la retroalimentación ni la respuesta correcta.
    """
    id = serializers.IntegerField()
    categoria_nombre = serializers.CharField()
    tipo = serializers.CharField()
    texto_base = serializers.CharField(allow_null=True)
    enunciado = serializers.CharField()
    puntaje = serializers.DecimalField(max_digits=5, decimal_places=2)
    orden = serializers.IntegerField()
    opciones = OpcionExamenSeguraSerializer(many=True)


class IntentoListSerializer(serializers.ModelSerializer):
    cuestionario_nombre = serializers.CharField(source='cuestionario.nombre', read_only=True)
    cuestionario_calificacion_maxima = serializers.DecimalField(source='cuestionario.calificacion_maxima', max_digits=5, decimal_places=2, read_only=True)
    cuestionario_permitir_revision = serializers.BooleanField(source='cuestionario.permitir_revision', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.get_full_name', read_only=True)
    estudiante_codigo = serializers.CharField(source='estudiante.codigo_estudiantil', read_only=True)

    class Meta:
        model = Intento
        fields = [
            'id', 'cuestionario', 'cuestionario_nombre',
            'cuestionario_calificacion_maxima', 'cuestionario_permitir_revision',
            'estudiante', 'estudiante_nombre', 'estudiante_codigo',
            'numero_intento', 'fecha_inicio', 'fecha_fin',
            'duracion_segundos', 'puntaje_obtenido', 'puntaje_total_posible',
            'calificacion', 'estado_intento', 'resultado',
            'total_preguntas', 'aciertos', 'errores', 'omitidas'
        ]


class RespuestaRevisionSerializer(serializers.ModelSerializer):
    """Serializer para la revisión pedagógica después de finalizar el examen."""
    enunciado = serializers.CharField(source='pregunta.enunciado', read_only=True)
    categoria_nombre = serializers.CharField(source='pregunta.categoria.nombre', read_only=True)
    texto_base = serializers.CharField(source='pregunta.texto_base', read_only=True)
    retroalimentacion = serializers.CharField(source='pregunta.retroalimentacion', read_only=True)
    opcion_seleccionada_letra = serializers.CharField(source='opcion_seleccionada.letra', default=None, read_only=True)
    opcion_seleccionada_texto = serializers.CharField(source='opcion_seleccionada.texto', default=None, read_only=True)
    opcion_correcta_letra = serializers.SerializerMethodField()
    opcion_correcta_texto = serializers.SerializerMethodField()
    todas_las_opciones = serializers.SerializerMethodField()

    class Meta:
        model = RespuestaIntento
        fields = [
            'id', 'pregunta_id', 'categoria_nombre', 'texto_base', 'enunciado',
            'opcion_seleccionada_letra', 'opcion_seleccionada_texto',
            'opcion_correcta_letra', 'opcion_correcta_texto',
            'es_acierto', 'puntaje_obtenido', 'marcada_revision',
            'retroalimentacion', 'todas_las_opciones'
        ]

    def get_opcion_correcta_letra(self, obj):
        corr = obj.pregunta.opciones.filter(es_correcta=True).first()
        return corr.letra if corr else None

    def get_opcion_correcta_texto(self, obj):
        corr = obj.pregunta.opciones.filter(es_correcta=True).first()
        return corr.texto if corr else None

    def get_todas_las_opciones(self, obj):
        return [
            {
                'id': opt.id,
                'letra': opt.letra,
                'texto': opt.texto,
                'es_correcta': opt.es_correcta
            }
            for opt in obj.pregunta.opciones.all().order_by('orden', 'letra')
        ]


class RevisionIntentoSerializer(serializers.ModelSerializer):
    """Resumen y desglose completo del intento para la pantalla de resultados."""
    cuestionario_nombre = serializers.CharField(source='cuestionario.nombre', read_only=True)
    cuestionario_calificacion_maxima = serializers.DecimalField(source='cuestionario.calificacion_maxima', max_digits=5, decimal_places=2, read_only=True)
    cuestionario_calificacion_aprobacion = serializers.DecimalField(source='cuestionario.calificacion_aprobacion', max_digits=5, decimal_places=2, read_only=True)
    permitir_revision = serializers.BooleanField(source='cuestionario.permitir_revision', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.get_full_name', read_only=True)
    estudiante_codigo = serializers.CharField(source='estudiante.codigo_estudiantil', read_only=True)
    respuestas = RespuestaRevisionSerializer(many=True, read_only=True)

    class Meta:
        model = Intento
        fields = [
            'id', 'cuestionario_id', 'cuestionario_nombre',
            'cuestionario_calificacion_maxima', 'cuestionario_calificacion_aprobacion',
            'permitir_revision', 'estudiante_nombre', 'estudiante_codigo',
            'numero_intento', 'fecha_inicio', 'fecha_fin', 'duracion_segundos',
            'puntaje_obtenido', 'puntaje_total_posible', 'calificacion',
            'estado_intento', 'resultado', 'total_preguntas',
            'aciertos', 'errores', 'omitidas', 'respuestas'
        ]
