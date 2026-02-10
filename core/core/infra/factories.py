from django.conf import settings


class ConsolaNotificador:
    """Notificador para entorno DEV que imprime en consola."""

    def enviar_confirmacion(self, suscripcion):
        print(f"[DEV] Suscripción creada: {suscripcion.id}")


class EmailNotificador:
    """Notificador para entorno PROD que envía emails reales."""

    def enviar_confirmacion(self, suscripcion):
        print(f"[PROD] Email enviado para suscripción {suscripcion.id}")


class NotificadorFactory:
    """Factory que selecciona el notificador según el entorno (DEV/PROD)."""

    @staticmethod
    def crear():
        if getattr(settings, "ENV_TYPE", "DEV") == "PROD":
            return EmailNotificador()
        return ConsolaNotificador()