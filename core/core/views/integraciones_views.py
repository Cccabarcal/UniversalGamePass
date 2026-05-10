"""
Vistas de integracion entre servicios:
- SistemaInfoAPI: Servicio a Proveer (endpoint JSON con info del sistema).
- AliadoInfoAPI / AliadoInfoView: Servicio a Consumir (equipo aliado).
- TerceraAPIView: Pagina HTML que consume API externa via Adapter.
"""
from datetime import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.infra.adapters import AllyClient, FreeToGameAdapter, GamesProvider
from core.models import Plan, Suscripcion, Videojuego


# ============================================================================
# Servicio a PROVEER (lo que otros equipos consumen de nosotros)
# ============================================================================
class SistemaInfoAPI(APIView):
    """
    GET /api/v1/sistema/info/

    Endpoint JSON con informacion publica del sistema. Es el "servicio a proveer"
    requerido por la entrega: cualquier equipo aliado puede consumirlo.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "sistema": settings.SYSTEM_NAME,
            "version": settings.SYSTEM_VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "estadisticas_publicas": {
                "planes_disponibles": Plan.objects.filter(activo=True).count(),
                "videojuegos_disponibles": Videojuego.objects.filter(disponible=True).count(),
                "suscripciones_activas": Suscripcion.objects.filter(activa=True).count(),
            },
            "endpoints_publicos": {
                "planes": "/api/v1/planes/",
                "videojuegos": "/api/v1/videojuegos/",
                "info": "/api/v1/sistema/info/",
            },
        })


# ============================================================================
# Servicio a CONSUMIR (lo que el equipo aliado expone)
# ============================================================================
class AliadoInfoAPI(APIView):
    """GET /api/v1/aliado/info/ - Devuelve la info que tomamos del equipo aliado."""
    permission_classes = [AllowAny]

    def get(self, request):
        client = AllyClient()
        return Response(client.obtener_info())


class AliadoInfoView(LoginRequiredMixin, View):
    """Pagina HTML que muestra la info del equipo aliado."""

    def get(self, request):
        client = AllyClient()
        return render(request, "core/integraciones/aliado.html", {
            "ally": client.obtener_info(),
            "ally_url": settings.ALLY_API_URL,
        })


# ============================================================================
# API de TERCEROS via Adapter (Inversion de Dependencias)
# ============================================================================
class TerceraAPIView(LoginRequiredMixin, View):
    """
    Vista HTML que muestra juegos populares obtenidos de un proveedor externo.
    Recibe el adapter por inyeccion (default: FreeToGameAdapter).
    """

    def __init__(self, provider: GamesProvider | None = None, **kwargs):
        super().__init__(**kwargs)
        self._provider = provider

    def get_provider(self) -> GamesProvider:
        return self._provider or FreeToGameAdapter()

    def get(self, request):
        provider = self.get_provider()
        juegos = provider.listar_juegos_populares(limit=6)
        return render(request, "core/integraciones/terceros.html", {
            "juegos": juegos,
            "fuente": getattr(settings, "THIRD_PARTY_GAMES_API_URL", ""),
        })
