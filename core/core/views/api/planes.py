"""
APIs REST para Planes
Endpoints específicos y desacoplados
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.models import Plan
from core.serializers import PlanSerializer
from core.utils.responses import APIResponse


class PlanListAPI(APIView):
    """
    GET /api/v1/planes/
    Listar todos los planes activos
    """
    permission_classes = [AllowAny]

    def get(self, request):
        planes = Plan.objects.filter(activo=True).order_by("nombre")
        serializer = PlanSerializer(planes, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Planes obtenidos exitosamente"
        )


class PlanDetailAPI(APIView):
    """
    GET /api/v1/planes/{id}/
    Obtener detalles de un plan específico
    """
    permission_classes = [AllowAny]

    def get(self, request, plan_id):
        plan = Plan.objects.filter(id=plan_id, activo=True).first()
        
        if not plan:
            return APIResponse.not_found("El plan solicitado no existe o no está disponible")
        
        serializer = PlanSerializer(plan)
        return APIResponse.success(
            data=serializer.data,
            message="Detalle del plan"
        )
