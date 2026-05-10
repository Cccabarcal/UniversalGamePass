"""
Factories de notificadores. Decide la implementacion segun el entorno (DEV/PROD).
- DEV  -> ConsolaNotificador
- PROD -> CeleryNotificador (asincrono via Redis)
- (fallback PROD sin Celery) -> EmailNotificador
"""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class ConsolaNotificador:
    """Notificador para entorno DEV que imprime en consola."""

    def enviar_confirmacion(self, suscripcion):
        print(f"[DEV] Suscripcion creada: {suscripcion.id}")


class EmailNotificador:
    """Notificador para entorno PROD que envia emails reales (placeholder)."""

    def enviar_confirmacion(self, suscripcion):
        logger.info("[PROD] Email enviado para suscripcion %s", suscripcion.id)


class CeleryNotificador:
    """Notificador asincrono que delega en Celery (Message Broker)."""

    def enviar_confirmacion(self, suscripcion):
        try:
            from core.tasks import notificar_suscripcion_creada
            notificar_suscripcion_creada.delay(
                suscripcion_id=suscripcion.id,
                username=suscripcion.user.username,
                plan_nombre=suscripcion.plan.nombre,
            )
        except Exception as exc:
            logger.warning("Fallback a EmailNotificador: %s", exc)
            EmailNotificador().enviar_confirmacion(suscripcion)


class NotificadorFactory:
    """Factory que selecciona el notificador segun el entorno."""

    @staticmethod
    def crear():
        env = getattr(settings, "ENV_TYPE", "DEV")
        if env == "PROD":
            return CeleryNotificador()
        return ConsolaNotificador()
