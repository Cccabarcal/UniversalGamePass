"""
APIs REST para Suscripciones
Endpoints específicos y desacoplados
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.models import Plan, Suscripcion
from core.serializers import SuscripcionListSerializer, SuscripcionCreateSerializer
from core.services import SuscripcionService
from core.infra.factories import NotificadorFactory
from core.utils.responses import APIResponse
from core.utils.validators import SuscripcionValidator


class SuscripcionListAPI(APIView):
    """
    GET /api/v1/suscripciones/
    Listar suscripciones del usuario autenticado
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suscripciones = Suscripcion.objects.filter(user=request.user).select_related(
            "user", "plan"
        )
        serializer = SuscripcionListSerializer(suscripciones, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Suscripciones obtenidas exitosamente"
        )


class SuscripcionDetailAPI(APIView):
    """
    GET /api/v1/suscripciones/{id}/
    Obtener detalles de una suscripción específica
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, suscripcion_id):
        suscripcion = Suscripcion.objects.filter(id=suscripcion_id).first()
        
        if not suscripcion:
            return APIResponse.not_found("La suscripción solicitada no existe")
        
        # Verificar que el usuario solo vea sus propias suscripciones
        if suscripcion.user != request.user:
            return APIResponse.forbidden("No tienes permiso para ver esta suscripción")
        
        serializer = SuscripcionListSerializer(suscripcion)
        return APIResponse.success(
            data=serializer.data,
            message="Detalle de la suscripción"
        )


class SuscripcionCreateAPI(APIView):
    """
    POST /api/v1/suscripciones/
    Crear una nueva suscripción
    Body: {"plan_id": 1, "renovacion_automatica": true}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SuscripcionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=serializer.errors,
                message="Los datos enviados no son válidos"
            )

        plan_id = serializer.validated_data.get("plan_id")
        
        # Obtener el plan
        plan = Plan.objects.filter(id=plan_id, activo=True).first()
        if not plan:
            return APIResponse.error(
                message="El plan solicitado no existe o no está disponible",
                error_code="PLAN_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Verificar suscripción activa duplicada
        existing = Suscripcion.objects.filter(
            user=request.user,
            plan_id=plan_id,
            activa=True
        ).first()

        validation_errors = SuscripcionValidator.validate_create(
            user=request.user,
            plan=plan,
            existing_suscripcion=existing
        )

        if validation_errors:
            return APIResponse.conflict(
                message=validation_errors.get('plan', 'No se pudo crear la suscripción'),
                conflict_code="DUPLICATE_SUBSCRIPTION"
            )

        # Crear suscripción
        service = SuscripcionService(notificador=NotificadorFactory.crear())
        try:
            suscripcion = service.crear_suscripcion(user=request.user, plan_id=plan_id)
            response_serializer = SuscripcionListSerializer(suscripcion)
            return APIResponse.created(
                data=response_serializer.data,
                message="Suscripción creada exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error al crear la suscripción: {str(e)}",
                error_code="CREATION_ERROR",
                status_code=status.HTTP_400_BAD_REQUEST
            )
