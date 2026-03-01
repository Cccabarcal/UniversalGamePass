from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .infra.factories import NotificadorFactory
from .models import Plan, Suscripcion, Videojuego, Transaccion
from .serializers import (
    PlanSerializer,
    SuscripcionListSerializer,
    SuscripcionCreateSerializer,
    VideojuegoSerializer,
    TransaccionSerializer,
)
from .services import SuscripcionService


class SignUpForm(UserCreationForm):
    """Formulario de registro con campos de username, email y contraseña."""
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class HomeView(View):
    """Página principal con opciones de login, registro y logout."""

    def get(self, request):
        return render(request, "core/home.html")


class SignUpView(CreateView):
    """Vista para registrar nuevos usuarios sin acceso al admin."""

    form_class = SignUpForm
    template_name = "core/signup.html"
    success_url = reverse_lazy("login")


class ProfileView(LoginRequiredMixin, View):
    """Vista para mostrar el perfil del usuario autenticado."""

    def get(self, request):
        return render(request, "core/profile.html", {"user": request.user})


class SuscripcionFormView(LoginRequiredMixin, View):
    """Vista que muestra el formulario para crear suscripciones."""

    def get(self, request):
        planes = Plan.objects.filter(activo=True).order_by("nombre")
        return render(request, "core/suscripcion_form.html", {"planes": planes})


class CrearSuscripcionView(LoginRequiredMixin, View):
    """Vista que procesa la creación de suscripciones con manejo de errores."""

    def post(self, request):
        plan_id = request.POST.get("plan_id")
        if not plan_id:
            messages.error(request, "Debe seleccionar un plan.")
            return redirect("suscripcion_form")

        service = SuscripcionService(notificador=NotificadorFactory.crear())
        try:
            service.crear_suscripcion(user=request.user, plan_id=plan_id)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("suscripcion_form")

        messages.success(request, "Suscripcion creada correctamente.")
        return redirect("suscripcion_form")



# Api rest endpoints



class PlanListAPIView(APIView):
    """
    API endpoint para listar todos los planes activos.
    GET /api/planes/
    """

    permission_classes = [AllowAny]

    def get(self, request):
        planes = Plan.objects.filter(activo=True).order_by("nombre")
        serializer = PlanSerializer(planes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlanDetailAPIView(APIView):
    """
    API endpoint para obtener detalles de un plan específico.
    GET /api/planes/{id}/
    """

    permission_classes = [AllowAny]

    def get(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        if not plan.activo:
            return Response(
                {"error": "El plan solicitado no está disponible."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideojuegoListAPIView(APIView):
    """
    API endpoint para listar todos los videojuegos disponibles.
    GET /api/videojuegos/
    """

    permission_classes = [AllowAny]

    def get(self, request):
        videojuegos = Videojuego.objects.filter(disponible=True).order_by("nombre")
        serializer = VideojuegoSerializer(videojuegos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VideojuegoDetailAPIView(APIView):
    """
    API endpoint para obtener detalles de un videojuego específico.
    GET /api/videojuegos/{id}/
    """

    permission_classes = [AllowAny]

    def get(self, request, videojuego_id):
        videojuego = get_object_or_404(Videojuego, id=videojuego_id)
        if not videojuego.disponible:
            return Response(
                {"error": "El videojuego solicitado no está disponible."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = VideojuegoSerializer(videojuego)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SuscripcionListAPIView(APIView):
    """
    API endpoint para listar suscripciones del usuario autenticado.
    GET /api/suscripciones/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        suscripciones = Suscripcion.objects.filter(user=request.user).select_related(
            "user", "plan"
        )
        serializer = SuscripcionListSerializer(suscripciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SuscripcionCreateAPIView(APIView):
    """
    API endpoint para crear una nueva suscripción.
    POST /api/suscripciones/crear/
    Body: {"plan_id": 1}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SuscripcionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        plan_id = serializer.validated_data.get("plan_id")

        # Validar que el usuario no tenga una suscripción activa al mismo plan (409 Conflict)
        if Suscripcion.objects.filter(
            user=request.user,
            plan_id=plan_id,
            activa=True
        ).exists():
            return Response(
                {
                    "error": "Ya tienes una suscripción activa a este plan.",
                    "conflict_code": "DUPLICATE_ACTIVE_SUBSCRIPTION"
                },
                status=status.HTTP_409_CONFLICT
            )

        service = SuscripcionService(notificador=NotificadorFactory.crear())
        try:
            suscripcion = service.crear_suscripcion(user=request.user, plan_id=plan_id)
            response_serializer = SuscripcionListSerializer(suscripcion)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )


class SuscripcionDetailAPIView(APIView):
    """
    API endpoint para obtener detalles de una suscripción específica.
    GET /api/suscripciones/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, suscripcion_id):
        suscripcion = get_object_or_404(Suscripcion, id=suscripcion_id)

        # Verificar que el usuario solo pueda ver sus propias suscripciones
        if suscripcion.user != request.user:
            return Response(
                {"error": "No tienes permiso para ver esta suscripción."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SuscripcionListSerializer(suscripcion)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransaccionListAPIView(APIView):
    """
    API endpoint para listar transacciones del usuario autenticado.
    GET /api/transacciones/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        transacciones = Transaccion.objects.filter(user=request.user).order_by("-fecha_creacion")
        serializer = TransaccionSerializer(transacciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransaccionDetailAPIView(APIView):
    """
    API endpoint para obtener detalles de una transacción específica.
    GET /api/transacciones/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, transaccion_id):
        transaccion = get_object_or_404(Transaccion, id=transaccion_id)

        # Verificar que el usuario solo pueda ver sus propias transacciones
        if transaccion.user != request.user:
            return Response(
                {"error": "No tienes permiso para ver esta transacción."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TransaccionSerializer(transaccion)
        return Response(serializer.data, status=status.HTTP_200_OK)
