from django.core.management.base import BaseCommand
from suscripciones.services import SuscripcionService


class Command(BaseCommand):
    help = 'Procesa renovaciones pendientes y envía notificaciones'

    def handle(self, *args, **kwargs):
        servicio = SuscripcionService()
        resultado = servicio.procesar_renovaciones_pendientes()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Notificaciones: {resultado['notificaciones_enviadas']}\n"
                f"✅ Expiraciones: {resultado['expiraciones_procesadas']}"
            )
        )