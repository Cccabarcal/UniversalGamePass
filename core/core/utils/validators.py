"""
Validadores reutilizables para la API
Lógica de validación desacoplada
"""

from datetime import datetime, timedelta
from .responses import APIResponse


class PlanValidator:
    """Validaciones para Planes"""

    @staticmethod
    def validate_create(data):
        """Valida datos para crear plan"""
        errors = {}

        if not data.get('nombre') or not str(data.get('nombre')).strip():
            errors['nombre'] = 'El nombre del plan es requerido'

        if not data.get('duracion_dias') or int(data.get('duracion_dias', 0)) <= 0:
            errors['duracion_dias'] = 'La duración debe ser mayor a 0 días'

        if not data.get('precio_mensual') or float(data.get('precio_mensual', 0)) < 0:
            errors['precio_mensual'] = 'El precio no puede ser negativo'

        return errors if errors else None


class SuscripcionValidator:
    """Validaciones para Suscripciones"""

    @staticmethod
    def validate_create(user, plan, existing_suscripcion=None):
        """Valida creación de suscripción"""
        errors = {}

        # Verificar que el usuario no tenga suscripción activa al mismo plan
        if existing_suscripcion:
            errors['plan'] = 'Ya tienes una suscripción activa a este plan'

        # Verificar que el plan sea válido
        if not plan.activo:
            errors['plan'] = 'El plan seleccionado no está disponible'

        return errors if errors else None


class VideojuegoValidator:
    """Validaciones para Videojuegos"""

    @staticmethod
    def validate_create(data):
        """Valida datos para crear videojuego"""
        errors = {}

        if not data.get('nombre') or not str(data.get('nombre')).strip():
            errors['nombre'] = 'El nombre del videojuego es requerido'

        if not data.get('genero') or not str(data.get('genero')).strip():
            errors['genero'] = 'El género es requerido'

        if data.get('precio_compra') and float(data.get('precio_compra', 0)) < 0:
            errors['precio_compra'] = 'El precio no puede ser negativo'

        return errors if errors else None


class TransaccionValidator:
    """Validaciones para Transacciones"""

    @staticmethod
    def validate_monto(monto):
        """Valida que el monto sea válido"""
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return 'El monto debe ser mayor a 0'
        except (ValueError, TypeError):
            return 'El monto debe ser un número'

        return None
