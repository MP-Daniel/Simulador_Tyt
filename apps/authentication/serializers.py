from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Rol, Permiso

Usuario = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado de JWT que incluye los datos del usuario,
    su rol y el listado de permisos activos en el payload del token y en la respuesta HTTP.
    Valida además que la cuenta no esté desactivada (Sec 2.1).
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Claims personalizados en el token JWT
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = user.get_full_name() or user.username
        token['codigo_estudiantil'] = user.codigo_estudiantil or ''
        token['programa_academico'] = user.programa_academico
        token['is_superuser'] = user.is_superuser
        token['is_active'] = user.is_active

        rol_data = None
        permisos_codigos = []
        if user.rol and user.rol.activo:
            rol_data = {
                'id': user.rol.id,
                'nombre': user.rol.nombre,
                'es_predeterminado': user.rol.es_predeterminado
            }
            permisos_codigos = list(user.rol.permisos.values_list('codigo', flat=True))
        elif user.is_superuser:
            rol_data = {'id': 0, 'nombre': 'Super Administrador', 'es_predeterminado': True}
            permisos_codigos = list(Permiso.objects.values_list('codigo', flat=True))

        token['rol'] = rol_data
        token['permisos'] = permisos_codigos

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'Esta cuenta de usuario ha sido desactivada por el administrador.'
            })

        # Datos adicionales en la respuesta JSON del login
        rol_nombre = user.rol.nombre if (user.rol and user.rol.activo) else ('Administrador' if user.is_superuser else 'Sin rol')
        permisos_list = []
        if user.is_superuser:
            permisos_list = list(Permiso.objects.values_list('codigo', flat=True))
        elif user.rol and user.rol.activo:
            permisos_list = list(user.rol.permisos.values_list('codigo', flat=True))

        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name() or user.username,
            'codigo_estudiantil': user.codigo_estudiantil or '',
            'programa_academico': user.programa_academico,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'rol': {
                'id': user.rol.id if user.rol else None,
                'nombre': rol_nombre
            },
            'permisos': permisos_list
        }
        return data


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'codigo', 'nombre', 'modulo', 'descripcion']


class RolSerializer(serializers.ModelSerializer):
    permisos_detalle = PermisoSerializer(source='permisos', many=True, read_only=True)
    permisos_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permiso.objects.all(),
        source='permisos',
        write_only=True,
        required=False
    )
    usuarios_count = serializers.IntegerField(source='usuarios.count', read_only=True)

    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 'es_predeterminado',
            'activo', 'permisos_detalle', 'permisos_ids',
            'usuarios_count', 'created_at', 'updated_at'
        ]

    def validate_nombre(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.es_predeterminado and instance.nombre != value:
            raise serializers.ValidationError("No se puede modificar el nombre de un rol predeterminado del sistema.")
        return value


class UsuarioSerializer(serializers.ModelSerializer):
    rol_detalle = RolSerializer(source='rol', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        source='rol',
        write_only=True,
        required=False,
        allow_null=True
    )
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'codigo_estudiantil', 'programa_academico', 'telefono',
            'is_active', 'rol_detalle', 'rol_id', 'password',
            'date_joined', 'last_login'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
