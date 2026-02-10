from django.shortcuts import get_object_or_404

from .domain.builders import SuscripcionBuilder
from .models import Plan


class SuscripcionService:
    """Servicio de aplicación para orquestar la creación de suscripciones.
    
    Coordina el flujo entre el Builder (construcción del modelo) y la Factory
    (inyección del notificador), aplicando inyección de dependencias.
    """

    def __init__(self, notificador):
        self.notificador = notificador

    def crear_suscripcion(self, user, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)

        suscripcion = (
            SuscripcionBuilder()
            .para_usuario(user)
            .con_plan(plan)
            .calcular_vigencia()
            .build()
        )

        self.notificador.enviar_confirmacion(suscripcion)
        return suscripcion