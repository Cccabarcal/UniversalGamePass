"""
Adapter Pattern: API de terceros para informacion de videojuegos populares.

Inversion de Dependencias:
- La aplicacion depende de la interfaz `GamesProvider` (abstracta).
- Las implementaciones concretas (`FreeToGameAdapter`, `FakeGamesAdapter`)
  se inyectan; pueden cambiarse sin tocar la logica de negocio.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

import requests
from django.conf import settings


class GamesProvider(ABC):
    """Puerto / interfaz que la app usa para obtener juegos populares."""

    @abstractmethod
    def listar_juegos_populares(self, limit: int = 6) -> List[Dict[str, Any]]:
        ...


class FreeToGameAdapter(GamesProvider):
    """
    Adapter sobre la API publica de FreeToGame (https://www.freetogame.com/api).
    No requiere API key y devuelve juegos free-to-play reales.

    Mapea el formato externo al contrato interno del proyecto.
    """

    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = base_url or settings.THIRD_PARTY_GAMES_API_URL
        self.timeout = timeout

    def listar_juegos_populares(self, limit: int = 6) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(self.base_url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            return [{
                "error": True,
                "mensaje": f"No se pudo consultar el proveedor externo: {exc}",
            }]

        juegos = []
        for raw in data[:limit]:
            juegos.append({
                "id_externo": raw.get("id"),
                "titulo": raw.get("title"),
                "genero": raw.get("genre"),
                "plataforma": raw.get("platform"),
                "imagen": raw.get("thumbnail"),
                "url": raw.get("game_url"),
                "fuente": "freetogame.com",
            })
        return juegos


class FakeGamesAdapter(GamesProvider):
    """Adapter de prueba (sin red) para tests y entornos offline."""

    def listar_juegos_populares(self, limit: int = 6) -> List[Dict[str, Any]]:
        catalogo = [
            {"id_externo": 1, "titulo": "Genshin Impact", "genero": "ARPG", "plataforma": "PC", "imagen": "", "url": "#", "fuente": "fake"},
            {"id_externo": 2, "titulo": "Warframe", "genero": "Shooter", "plataforma": "PC", "imagen": "", "url": "#", "fuente": "fake"},
            {"id_externo": 3, "titulo": "Lost Ark", "genero": "MMORPG", "plataforma": "PC", "imagen": "", "url": "#", "fuente": "fake"},
        ]
        return catalogo[:limit]
