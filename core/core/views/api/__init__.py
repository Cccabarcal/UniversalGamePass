"""
APIs REST por recurso
"""

from .planes import PlanListAPI, PlanDetailAPI
from .videojuegos import VideojuegoListAPI, VideojuegoDetailAPI
from .suscripciones import SuscripcionListAPI, SuscripcionDetailAPI, SuscripcionCreateAPI
from .transacciones import TransaccionListAPI, TransaccionDetailAPI, TransaccionEstadisticasAPI

__all__ = [
    'PlanListAPI', 'PlanDetailAPI',
    'VideojuegoListAPI', 'VideojuegoDetailAPI',
    'SuscripcionListAPI', 'SuscripcionDetailAPI', 'SuscripcionCreateAPI',
    'TransaccionListAPI', 'TransaccionDetailAPI', 'TransaccionEstadisticasAPI',
]
