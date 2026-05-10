"""
Tareas asincronas de Celery para procesos de fondo.

Ejemplos:
- Notificacion de suscripcion creada (email/log).
- Generacion de reporte de uso (consumiendo el microservicio Flask).
"""
import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(name="core.tasks.notificar_suscripcion_creada")
def notificar_suscripcion_creada(suscripcion_id: int, username: str, plan_nombre: str):
    """Procesa una notificacion de suscripcion en background."""
    logger.info(
        "[Celery] Notificacion de suscripcion %s para %s en plan %s",
        suscripcion_id, username, plan_nombre,
    )
    return {
        "ok": True,
        "suscripcion_id": suscripcion_id,
        "user": username,
        "plan": plan_nombre,
    }


@shared_task(name="core.tasks.generar_reporte_usuario")
def generar_reporte_usuario(user_id: int):
    """Lanza un reporte asincrono consumiendo el microservicio Flask."""
    import requests

    base = "http://flask_reports:5000"
    url = f"{base}/api/v2/reportes/estadisticas-usuario/{user_id}"
    try:
        resp = requests.get(url, timeout=settings.ALLY_API_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        logger.info("[Celery] Reporte generado para user %s: %s", user_id, data)
        return data
    except Exception as exc:
        logger.exception("[Celery] Error al generar reporte: %s", exc)
        return {"error": str(exc)}
