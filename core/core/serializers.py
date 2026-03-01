from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Videojuego, Plan, Suscripcion, Transaccion


class UserSerializer(serializers.ModelSerializer):
    """Serializador para la entidad User con información pública."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class VideojuegoSerializer(serializers.ModelSerializer):
    """Serializador para la entidad Videojuego."""

    class Meta:
        model = Videojuego
        fields = ['id', 'nombre', 'descripcion', 'genero', 'imagen_url', 'precio_compra', 'disponible', 'fecha_lanzamiento', 'creado_en']
        read_only_fields = ['id', 'creado_en']

    def validate_genero(self, value):
        """Valida que el género no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El género no puede estar vacío.")
        return value


class PlanSerializer(serializers.ModelSerializer):
    """Serializador para la entidad Plan con validaciones de negocio."""

    class Meta:
        model = Plan
        fields = ['id', 'nombre', 'duracion_dias', 'precio_mensual', 'descripcion', 'activo', 'creado_en']
        read_only_fields = ['id', 'creado_en']

    def validate_duracion_dias(self, value):
        """Valida que la duración sea positiva."""
        if value <= 0:
            raise serializers.ValidationError("La duración debe ser mayor a 0 días.")
        return value

    def validate_precio_mensual(self, value):
        """Valida que el precio sea positivo."""
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value


class SuscripcionListSerializer(serializers.ModelSerializer):
    """Serializador de lectura para mostrar suscripciones con datos relacionados."""

    user = UserSerializer(read_only=True)
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Suscripcion
        fields = ['id', 'user', 'plan', 'inicio', 'fin', 'activa', 'renovacion_automatica']
        read_only_fields = ['id', 'inicio', 'fin']


class SuscripcionCreateSerializer(serializers.ModelSerializer):
    """Serializador para creación de suscripciones (solo acepta plan_id)."""

    plan_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Suscripcion
        fields = ['plan_id', 'renovacion_automatica']

    def validate_plan_id(self, value):
        """Valida que el plan exista y esté activo."""
        try:
            plan = Plan.objects.get(id=value)
            if not plan.activo:
                raise serializers.ValidationError("El plan seleccionado no está disponible.")
        except Plan.DoesNotExist:
            raise serializers.ValidationError("El plan no existe.")
        return value


class TransaccionSerializer(serializers.ModelSerializer):
    """Serializador para la entidad Transaccion."""

    user = UserSerializer(read_only=True)
    plan_nombre = serializers.CharField(source='suscripcion.plan.nombre', read_only=True)
    videojuego_nombre = serializers.CharField(source='videojuego.nombre', read_only=True)

    class Meta:
        model = Transaccion
        fields = ['id', 'user', 'monto', 'tipo', 'estado', 'referencia_externa', 'fecha_creacion', 'fecha_completada', 'descripcion', 'plan_nombre', 'videojuego_nombre']
        read_only_fields = ['id', 'user', 'fecha_creacion']

    def validate_monto(self, value):
        """Valida que el monto sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
