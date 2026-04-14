"""
APIs REST para Transacciones
Endpoints específicos y desacoplados
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.models import Transaccion
from core.serializers import TransaccionSerializer
from core.utils.responses import APIResponse


class TransaccionListAPI(APIView):
    """
    GET /api/v1/transacciones/
    Listar transacciones del usuario autenticado
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transacciones = Transaccion.objects.filter(user=request.user).order_by("-fecha_creacion")
        serializer = TransaccionSerializer(transacciones, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Transacciones obtenidas exitosamente"
        )


class TransaccionDetailAPI(APIView):
    """
    GET /api/v1/transacciones/{id}/
    Obtener detalles de una transacción específica
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, transaccion_id):
        transaccion = Transaccion.objects.filter(id=transaccion_id).first()
        
        if not transaccion:
            return APIResponse.not_found("La transacción solicitada no existe")
        
        # Verificar que el usuario solo vea sus propias transacciones
        if transaccion.user != request.user:
            return APIResponse.forbidden("No tienes permiso para ver esta transacción")
        
        serializer = TransaccionSerializer(transaccion)
        return APIResponse.success(
            data=serializer.data,
            message="Detalle de la transacción"
        )


class TransaccionEstadisticasAPI(APIView):
    """
    GET /api/v1/transacciones/estadisticas/
    Estadísticas de transacciones del usuario
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transacciones = Transaccion.objects.filter(user=request.user)
        
        stats = {
            "total_transacciones": transacciones.count(),
            "total_gastado": sum(t.monto for t in transacciones if t.estado == 'completada'),
            "por_estado": {
                "completadas": transacciones.filter(estado='completada').count(),
                "pendientes": transacciones.filter(estado='pendiente').count(),
                "fallidas": transacciones.filter(estado='fallida').count(),
                "canceladas": transacciones.filter(estado='cancelada').count(),
            }
        }
        
        return APIResponse.success(
            data=stats,
            message="Estadísticas de transacciones"
        )
