"""
Vistas de Django para templates HTML
Vistas tradicionales (no API REST)
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from core.infra.factories import NotificadorFactory
from core.models import Plan, Suscripcion, Transaccion
from core.services import SuscripcionService, obtener_suscripcion_activa


class SignUpForm(UserCreationForm):
    """Formulario de registro con campos de username, email y contrasena."""

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class HomeView(View):
    """Pagina principal con opciones de login, registro y logout."""

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
        suscripciones = Suscripcion.objects.filter(user=request.user)
        transacciones = Transaccion.objects.filter(user=request.user)[:10]
        suscripcion_activa = obtener_suscripcion_activa(request.user)

        return render(request, "core/profile.html", {
            "user": request.user,
            "suscripciones": suscripciones,
            "transacciones": transacciones,
            "suscripcion_activa": suscripcion_activa,
        })


class SuscripcionFormView(LoginRequiredMixin, View):
    """Muestra el formulario para crear/cambiar suscripciones."""

    def get(self, request):
        planes = Plan.objects.filter(activo=True).order_by("nombre")
        suscripcion_activa = obtener_suscripcion_activa(request.user)
        return render(request, "core/suscripcion_form.html", {
            "planes": planes,
            "suscripcion_activa": suscripcion_activa,
        })


class CrearSuscripcionView(LoginRequiredMixin, View):
    """Procesa la creacion (o cambio) de suscripciones."""

    def post(self, request):
        plan_id = request.POST.get("plan_id")
        if not plan_id:
            messages.error(request, "Debe seleccionar un plan.")
            return redirect("suscripcion_form")

        service = SuscripcionService(notificador=NotificadorFactory.crear())
        try:
            suscripcion = service.crear_suscripcion(user=request.user, plan_id=plan_id)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("suscripcion_form")

        messages.success(
            request,
            f"Suscripcion al plan '{suscripcion.plan.nombre}' creada correctamente.",
        )
        return redirect("profile")


class CancelarSuscripcionView(LoginRequiredMixin, View):
    """Cancela la suscripcion activa del usuario (o una especifica via id)."""

    def post(self, request):
        suscripcion_id = request.POST.get("suscripcion_id") or None
        service = SuscripcionService(notificador=NotificadorFactory.crear())
        try:
            sub = service.cancelar_suscripcion(
                user=request.user,
                suscripcion_id=int(suscripcion_id) if suscripcion_id else None,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("profile")

        messages.success(
            request,
            f"Has cancelado tu suscripcion al plan '{sub.plan.nombre}'.",
        )
        return redirect("profile")
