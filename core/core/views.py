from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from .infra.factories import NotificadorFactory
from .models import Plan
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