"""
Cliente para consumir el endpoint del equipo aliado.
URL configurable via ALLY_API_URL en settings/env.
"""
from typing import Any, Dict

import requests
from django.conf import settings


class AllyClient:
    """Cliente que consume el endpoint JSON del equipo aliado."""

    def __init__(self, url: str | None = None, timeout: int | None = None):
        self.url = url if url is not None else settings.ALLY_API_URL
        self.timeout = timeout if timeout is not None else settings.ALLY_API_TIMEOUT

    def disponible(self) -> bool:
        return bool(self.url)

    def obtener_info(self) -> Dict[str, Any]:
        if not self.disponible():
            return {
                "configurado": False,
                "mensaje": "ALLY_API_URL no configurada todavia. "
                           "Define ALLY_API_URL en el entorno cuando el equipo aliado publique su URL.",
            }
        try:
            resp = requests.get(self.url, timeout=self.timeout)
            resp.raise_for_status()
            return {
                "configurado": True,
                "url": self.url,
                "status_code": resp.status_code,
                "data": resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else resp.text,
            }
        except Exception as exc:
            return {
                "configurado": True,
                "url": self.url,
                "error": str(exc),
            }
