from rest_framework import serializers
from decimal import Decimal
from .models import Cuestionario, CuestionarioPregunta
from banco_preguntas.serializers import PreguntaDetalleSerializer


class CuestionarioPreguntaSerializer(serializers.ModelSerializer):
    pregunta_detalle = PreguntaDetalleSerializer(source='pregunta', read_only=True)

    class Meta:
        model = CuestionarioPregunta
        fields = ['id', 'pregunta', 'pregunta_detalle', 'puntaje', 'orden']


class CuestionarioSerializer(serializers.ModelSerializer):
    """Serializer administrativo para creación, edición y consulta de cuestionarios."""
    cuestionario_preguntas = CuestionarioPreguntaSerializer(many=True, read_only=True)
    total_preguntas = serializers.IntegerField(source='cuestionario_preguntas.count', read_only=True)
    puntaje_total = serializers.DecimalField(source='puntaje_total_posible', max_digits=7, decimal_places=2, read_only=True)
    preguntas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Cuestionario
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_apertura', 'fecha_cierre',
            'tiempo_limite_minutos', 'intentos_permitidos', 'calificacion_maxima',
            'calificacion_aprobacion', 'mezclar_preguntas', 'mezclar_respuestas',
            'permitir_revision', 'estado', 'activo', 'total_preguntas',
            'puntaje_total', 'cuestionario_preguntas', 'preguntas_ids',
            'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        apertura = attrs.get('fecha_apertura', getattr(self.instance, 'fecha_apertura', None))
        cierre = attrs.get('fecha_cierre', getattr(self.instance, 'fecha_cierre', None))
        maxima = attrs.get('calificacion_maxima', getattr(self.instance, 'calificacion_maxima', Decimal('5.00')))
        aprobacion = attrs.get('calificacion_aprobacion', getattr(self.instance, 'calificacion_aprobacion', Decimal('3.00')))

        if apertura and cierre and cierre <= apertura:
            raise serializers.ValidationError({
                'fecha_cierre': 'Regla R01 violada: La fecha de cierre debe ser posterior a la fecha de apertura.'
            })

        if maxima is not None and maxima <= Decimal('0.00'):
            raise serializers.ValidationError({
                'calificacion_maxima': 'Regla R02 violada: La calificación máxima debe ser mayor que cero.'
            })

        if aprobacion is not None and maxima is not None:
            if aprobacion < Decimal('0.00') or aprobacion > maxima:
                raise serializers.ValidationError({
                    'calificacion_aprobacion': 'Regla R03 violada: La nota de aprobación debe estar entre 0.00 y la calificación máxima.'
                })

        return attrs

    def create(self, validated_data):
        preguntas_ids = validated_data.pop('preguntas_ids', [])
        cuestionario = Cuestionario.objects.create(**validated_data)

        from banco_preguntas.models import Pregunta
        for idx, p_id in enumerate(preguntas_ids, 1):
            try:
                pregunta = Pregunta.objects.get(id=p_id)
                CuestionarioPregunta.objects.create(
                    cuestionario=cuestionario,
                    pregunta=pregunta,
                    puntaje=pregunta.puntaje,
                    orden=idx
                )
            except Pregunta.DoesNotExist:
                continue

        return cuestionario

    def update(self, instance, validated_data):
        preguntas_ids = validated_data.pop('preguntas_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if preguntas_ids is not None:
            instance.cuestionario_preguntas.all().delete()
            from banco_preguntas.models import Pregunta
            for idx, p_id in enumerate(preguntas_ids, 1):
                try:
                    pregunta = Pregunta.objects.get(id=p_id)
                    CuestionarioPregunta.objects.create(
                        cuestionario=instance,
                        pregunta=pregunta,
                        puntaje=pregunta.puntaje,
                        orden=idx
                    )
                except Pregunta.DoesNotExist:
                    continue

        return instance


class CuestionarioEstudianteSerializer(serializers.ModelSerializer):
    """
    Serializer para el portal del estudiante (Sec 2.5).
    Expone los cuestionarios disponibles y audita intentos consumidos.
    """
    total_preguntas = serializers.IntegerField(source='cuestionario_preguntas.count', read_only=True)
    disponible_ahora = serializers.SerializerMethodField()
    motivo_no_disponible = serializers.SerializerMethodField()
    intentos_realizados = serializers.SerializerMethodField()
    puede_iniciar = serializers.SerializerMethodField()

    class Meta:
        model = Cuestionario
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_apertura', 'fecha_cierre',
            'tiempo_limite_minutos', 'intentos_permitidos', 'calificacion_maxima',
            'calificacion_aprobacion', 'total_preguntas', 'disponible_ahora',
            'motivo_no_disponible', 'intentos_realizados', 'puede_iniciar'
        ]

    def get_disponible_ahora(self, obj):
        disponible, _ = obj.esta_disponible_ahora()
        return disponible

    def get_motivo_no_disponible(self, obj):
        _, motivo = obj.esta_disponible_ahora()
        return motivo

    def get_intentos_realizados(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if not user or not user.is_authenticated:
            return 0
        from evaluaciones.models import Intento
        return Intento.objects.filter(cuestionario=obj, estudiante=user).count()

    def get_puede_iniciar(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if not user or not user.is_authenticated:
            return False
        puede, _ = obj.puede_iniciar_estudiante(user)
        return puede
