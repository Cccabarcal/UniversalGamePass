from django.conf import settings

class ConsolaNotificador:
    def enviar_confirmacion(self, suscripcion):
        print(f"[DEV] Suscripción creada: {suscripcion.id}")

class EmailNotificador:
    def enviar_confirmacion(self, suscripcion):
        # Simulación de envío real
        print(f"[PROD] Email enviado para suscripción {suscripcion.id}")

class NotificadorFactory:
    @staticmethod
    def crear():
        if getattr(settings, "ENV_TYPE", "DEV") == "PROD":
            return EmailNotificador()
        return ConsolaNotificador()