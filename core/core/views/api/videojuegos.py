"""
APIs REST para Videojuegos
Endpoints específicos y desacoplados
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.models import Videojuego
from core.serializers import VideojuegoSerializer
from core.utils.responses import APIResponse


class VideojuegoListAPI(APIView):
    """
    GET /api/v1/videojuegos/
    Listar todos los videojuegos disponibles
    """
    permission_classes = [AllowAny]

    def get(self, request):
        videojuegos = Videojuego.objects.filter(disponible=True).order_by("nombre")
        serializer = VideojuegoSerializer(videojuegos, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Videojuegos obtenidos exitosamente"
        )


class VideojuegoDetailAPI(APIView):
    """
    GET /api/v1/videojuegos/{id}/
    Obtener detalles de un videojuego específico
    """
    permission_classes = [AllowAny]

    def get(self, request, videojuego_id):
        videojuego = Videojuego.objects.filter(id=videojuego_id, disponible=True).first()
        
        if not videojuego:
            return APIResponse.not_found("El videojuego solicitado no existe o no está disponible")
        
        serializer = VideojuegoSerializer(videojuego)
        return APIResponse.success(
            data=serializer.data,
            message="Detalle del videojuego"
        )
