"""
Vistas del proyecto - Web y API
"""

from .web_views import (
    HomeView,
    SignUpView,
    SignUpForm,
    ProfileView,
    SuscripcionFormView,
    CrearSuscripcionView,
    CancelarSuscripcionView,
)
from .juegos_views import (
    CatalogoJuegosView,
    RAWGHubView,
    JugarView,
    CrearJuegoView,
    VideojuegoForm,
)
from .integraciones_views import (
    SistemaInfoAPI,
    AliadoInfoAPI,
    AliadoInfoView,
    TerceraAPIView,
)

__all__ = [
    'HomeView', 'SignUpView', 'SignUpForm', 'ProfileView',
    'SuscripcionFormView', 'CrearSuscripcionView', 'CancelarSuscripcionView',
    'CatalogoJuegosView', 'RAWGHubView', 'JugarView', 'CrearJuegoView', 'VideojuegoForm',
    'SistemaInfoAPI', 'AliadoInfoAPI', 'AliadoInfoView', 'TerceraAPIView',
]
