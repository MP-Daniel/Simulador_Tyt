from rest_framework import serializers
from decimal import Decimal
from .models import Categoria, Pregunta, OpcionRespuesta, Importacion


class CategoriaSerializer(serializers.ModelSerializer):
    preguntas_count = serializers.IntegerField(source='preguntas.count', read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo', 'preguntas_count', 'created_at']


class OpcionRespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionRespuesta
        fields = ['id', 'letra', 'texto', 'es_correcta', 'orden']


class PreguntaDetalleSerializer(serializers.ModelSerializer):
    """Serializer para administración del banco: incluye opciones con su marca de es_correcta."""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    opciones = OpcionRespuestaSerializer(many=True, required=False)

    class Meta:
        model = Pregunta
        fields = [
            'id', 'categoria', 'categoria_nombre', 'tipo',
            'texto_base', 'enunciado', 'retroalimentacion',
            'puntaje', 'activo', 'opciones', 'created_at', 'updated_at'
        ]

    def validate_puntaje(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("El puntaje debe ser mayor que cero (Regla R02).")
        return value

    def create(self, validated_data):
        opciones_data = self.initial_data.get('opciones', [])
        pregunta = Pregunta.objects.create(**validated_data)

        # Crear opciones asociadas
        correct_count = 0
        for opt in opciones_data:
            es_corr = bool(opt.get('es_correcta', False))
            if es_corr:
                correct_count += 1
            OpcionRespuesta.objects.create(
                pregunta=pregunta,
                letra=str(opt.get('letra', '')).strip().upper(),
                texto=str(opt.get('texto', '')).strip(),
                es_correcta=es_corr,
                orden=int(opt.get('orden', 1))
            )

        # Regla R05: Validar que exista al menos una opción correcta si se enviaron opciones
        if opciones_data and correct_count != 1:
            raise serializers.ValidationError("Regla R05: Cada pregunta debe tener exactamente una sola respuesta correcta.")

        return pregunta

    def update(self, instance, validated_data):
        opciones_data = self.initial_data.get('opciones', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if opciones_data is not None:
            # Reemplazar opciones
            correct_count = 0
            instance.opciones.all().delete()
            for opt in opciones_data:
                es_corr = bool(opt.get('es_correcta', False))
                if es_corr:
                    correct_count += 1
                OpcionRespuesta.objects.create(
                    pregunta=instance,
                    letra=str(opt.get('letra', '')).strip().upper(),
                    texto=str(opt.get('texto', '')).strip(),
                    es_correcta=es_corr,
                    orden=int(opt.get('orden', 1))
                )
            if correct_count != 1:
                raise serializers.ValidationError("Regla R05: Cada pregunta debe tener exactamente una sola respuesta correcta.")

        return instance


class ImportacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Importacion
        fields = [
            'id', 'archivo_nombre', 'fecha', 'total_filas',
            'filas_validas', 'filas_duplicadas', 'filas_error',
            'detalles_errores', 'usuario_nombre'
        ]
