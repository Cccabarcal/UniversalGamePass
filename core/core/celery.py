"""
Configuracion de Celery para UniversalGamePass.

Carga la configuracion desde Django settings con prefijo CELERY_*.
Las tareas asincronas se descubren automaticamente desde core/tasks.py
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("universalgamepass")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
