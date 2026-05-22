"""
Adapter Pattern: API de terceros para informacion de videojuegos.

Inversion de Dependencias:
- La aplicacion depende de la interfaz `GamesProvider` (abstracta).
- Las implementaciones concretas (FreeToGameAdapter, RAWGAdapter, FakeGamesAdapter)
  se inyectan; pueden cambiarse sin tocar la logica de negocio.

RAWG.io: Base de datos masiva de juegos con metadata profesional, ratings, screenshots.
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


class RAWGAdapter(GamesProvider):
    """
    Adapter sobre RAWG.io API (https://rawg.io/api).
    Base de datos profesional con metadata completa, ratings, screenshots.
    
    No requiere API key para requests básicas (límite: 20 req/min).
    Devuelve juegos nuevos ordenados por fecha de lanzamiento.
    """

    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = base_url or f"{settings.RAWG_API_URL}/games"
        self.timeout = timeout
        self.api_key = settings.RAWG_API_KEY

    def listar_juegos_populares(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Trae juegos populares ordenados por rating."""
        try:
            # RAWG.io requiere API key obligatoria
            params = {
                "ordering": "-rating",
                "page_size": limit,
                "key": self.api_key,  # API key es obligatoria
            }

            print(f"[DEBUG] RAWG Request URL: {self.base_url}")
            print(f"[DEBUG] RAWG Params: {params}")

            resp = requests.get(self.base_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"[DEBUG] RAWG Success: {len(data.get('results', []))} juegos encontrados")
            
        except Exception as exc:
            print(f"[ERROR] RAWG API failed: {type(exc).__name__}: {exc}")
            print(f"[INFO] Usando datos locales como fallback")
            return []  # Retornar lista vacía para trigger fallback

        juegos = []
        for raw in data.get("results", [])[:limit]:
            # Mapear géneros
            generos = ", ".join([g["name"] for g in raw.get("genres", [])])
            
            # Mapear plataformas
            plataformas = ", ".join([p["platform"]["name"] for p in raw.get("platforms", [])])
            
            juegos.append({
                "id_externo": raw.get("id"),
                "titulo": raw.get("name"),
                "genero": generos or "Variado",
                "plataforma": plataformas or "Múltiples",
                "imagen": raw.get("background_image", ""),
                "url": f"https://rawg.io/games/{raw.get('slug', '')}",
                "fuente": "rawg.io",
                "rating": raw.get("rating", 0),
                "metacritic": raw.get("metacritic"),
                "descripcion": raw.get("description_raw", "")[:150] if raw.get("description_raw") else "",
                "fecha_lanzamiento": raw.get("released", ""),
            })
        
        return juegos


class FakeGamesAdapter(GamesProvider):
    """Adapter con datos simulados de RAWG.io para testing y cuando API falla."""

    def listar_juegos_populares(self, limit: int = 6) -> List[Dict[str, Any]]:
        catalogo = [
            {
                "id_externo": 3498,
                "titulo": "Hades",
                "genero": "Action, Indie",
                "plataforma": "PC, PlayStation 4, Nintendo Switch",
                "imagen": "https://media.rawg.io/media/games/198/198ffc34b8b0e738dd311e9431b2b1a7.jpg",
                "url": "https://rawg.io/games/hades",
                "fuente": "rawg.io",
                "rating": 4.55,
                "metacritic": 93,
                "descripcion": "Hades is a roguelike dungeon crawler where you play as the prince of the underworld",
                "fecha_lanzamiento": "2020-09-17",
            },
            {
                "id_externo": 5286,
                "titulo": "Hollow Knight",
                "genero": "Adventure, Indie",
                "plataforma": "PC, Nintendo Switch, PlayStation 4",
                "imagen": "https://media.rawg.io/media/games/511/5118aff5091cb3efb259841f1a131fbb.jpg",
                "url": "https://rawg.io/games/hollow-knight",
                "fuente": "rawg.io",
                "rating": 4.54,
                "metacritic": 86,
                "descripcion": "Hollow Knight is a 2D adventure game set in the grim, alien world of Hallownest",
                "fecha_lanzamiento": "2017-02-24",
            },
            {
                "id_externo": 13633,
                "titulo": "Elden Ring",
                "genero": "Action, Adventure, RPG",
                "plataforma": "PC, PlayStation 4, PlayStation 5, Xbox One",
                "imagen": "https://media.rawg.io/media/games/511/5118aff5091cb3efb259841f1a131fbb.jpg",
                "url": "https://rawg.io/games/elden-ring",
                "fuente": "rawg.io",
                "rating": 4.5,
                "metacritic": 96,
                "descripcion": "Rise, Tarnished, and let grace guide thee. A new masterpiece from FromSoftware.",
                "fecha_lanzamiento": "2022-02-25",
            },
            {
                "id_externo": 4200,
                "titulo": "Portal 2",
                "genero": "Adventure, Puzzle",
                "plataforma": "PC, PlayStation 3, Xbox 360",
                "imagen": "https://media.rawg.io/media/games/020/0205f5eb1d328ce976e43cfe43899cc5.jpg",
                "url": "https://rawg.io/games/portal-2",
                "fuente": "rawg.io",
                "rating": 4.49,
                "metacritic": 95,
                "descripcion": "The puzzle-platform game Portal returns with a new chapter in the award-winning series.",
                "fecha_lanzamiento": "2011-05-04",
            },
            {
                "id_externo": 319,
                "titulo": "Half-Life 2",
                "genero": "Action, Adventure, Shooter",
                "plataforma": "PC, PlayStation 2, Xbox",
                "imagen": "https://media.rawg.io/media/games/6cd/6cd653e0aashow.jpg",
                "url": "https://rawg.io/games/half-life-2",
                "fuente": "rawg.io",
                "rating": 4.48,
                "metacritic": 96,
                "descripcion": "Half-Life 2 is a science fiction first-person shooter.",
                "fecha_lanzamiento": "2004-11-16",
            },
            {
                "id_externo": 3070,
                "titulo": "The Legend of Zelda: Breath of the Wild",
                "genero": "Adventure, Action, Puzzle",
                "plataforma": "Nintendo Switch, Wii U",
                "imagen": "https://media.rawg.io/media/games/26d/26d548c4c2da328da24ed46aa41aa68f.jpg",
                "url": "https://rawg.io/games/the-legend-of-zelda-breath-of-the-wild",
                "fuente": "rawg.io",
                "rating": 4.46,
                "metacritic": 97,
                "descripcion": "Forget everything you know about The Legend of Zelda games.",
                "fecha_lanzamiento": "2017-03-03",
            },
        ]
        return catalogo[:limit]
