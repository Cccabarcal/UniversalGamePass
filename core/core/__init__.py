# Cargamos la app de Celery cuando arranca Django para que @shared_task funcione.
try:
    from .celery import app as celery_app  # noqa: F401
except ImportError:
    # Celery puede no estar instalado en algunos entornos (tests)
    celery_app = None

__all__ = ("celery_app",)
