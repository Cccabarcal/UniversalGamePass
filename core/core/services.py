from django.shortcuts import get_object_or_404
from django.utils import timezone

from .domain.builders import SuscripcionBuilder
from .models import Plan, Suscripcion


def usuario_tiene_suscripcion_activa(user):
    """Devuelve True si el usuario posee al menos una suscripcion vigente."""
    if not user.is_authenticated:
        return False
    ahora = timezone.now()
    return Suscripcion.objects.filter(
        user=user,
        activa=True,
        inicio__lte=ahora,
        fin__gte=ahora,
    ).exists()


def obtener_suscripcion_activa(user):
    """Devuelve la suscripcion activa vigente del usuario, o None."""
    if not user.is_authenticated:
        return None
    ahora = timezone.now()
    return (
        Suscripcion.objects.filter(
            user=user,
            activa=True,
            inicio__lte=ahora,
            fin__gte=ahora,
        )
        .select_related("plan")
        .order_by("-fin")
        .first()
    )


class SuscripcionService:
    """Servicio de aplicacion para orquestar la creacion de suscripciones.

    Coordina el flujo entre el Builder (construccion del modelo) y la Factory
    (inyeccion del notificador), aplicando inyeccion de dependencias.
    """

    def __init__(self, notificador):
        self.notificador = notificador

    def crear_suscripcion(self, user, plan_id):
        """Crea o cambia la suscripcion del usuario.

        - Si ya tiene una suscripcion activa con el MISMO plan -> ValueError.
        - Si tiene otra suscripcion activa con plan distinto -> la cancela
          (cambio de plan) y crea la nueva.
        - Si no tiene ninguna -> crea normalmente.
        """
        plan = get_object_or_404(Plan, id=plan_id)

        activa_existente = obtener_suscripcion_activa(user)
        if activa_existente:
            if activa_existente.plan_id == plan.id:
                raise ValueError(
                    f"Ya tienes una suscripcion activa al plan '{plan.nombre}'."
                )
            # Cambio de plan: cancelamos la actual antes de crear la nueva.
            self._desactivar(activa_existente)

        suscripcion = (
            SuscripcionBuilder()
            .para_usuario(user)
            .con_plan(plan)
            .calcular_vigencia()
            .build()
        )

        self.notificador.enviar_confirmacion(suscripcion)
        return suscripcion

    def cancelar_suscripcion(self, user, suscripcion_id=None):
        """Cancela la suscripcion indicada, o la activa actual si no se indica."""
        if suscripcion_id is not None:
            suscripcion = get_object_or_404(
                Suscripcion, id=suscripcion_id, user=user
            )
        else:
            suscripcion = obtener_suscripcion_activa(user)
            if suscripcion is None:
                raise ValueError("No tienes una suscripcion activa para cancelar.")

        if not suscripcion.activa:
            raise ValueError("La suscripcion ya estaba cancelada.")

        self._desactivar(suscripcion)
        return suscripcion

    @staticmethod
    def _desactivar(suscripcion):
        suscripcion.activa = False
        suscripcion.renovacion_automatica = False
        suscripcion.fin = timezone.now()
        suscripcion.save(update_fields=["activa", "renovacion_automatica", "fin"])
