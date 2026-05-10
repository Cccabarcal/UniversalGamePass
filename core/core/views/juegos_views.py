"""
Vistas web para el módulo de Videojuegos:
- Catálogo (listar)
- Jugar (ejecutar el juego HTML5)
- Crear (solo staff)
"""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from core.models import Videojuego
from core.services import usuario_tiene_suscripcion_activa


class VideojuegoForm(forms.ModelForm):
    """Formulario para que el staff registre nuevos videojuegos."""

    class Meta:
        model = Videojuego
        fields = [
            "nombre",
            "descripcion",
            "genero",
            "imagen_url",
            "precio_compra",
            "disponible",
            "fecha_lanzamiento",
            "slug_ejecutable",
            "requiere_suscripcion",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "fecha_lanzamiento": forms.DateInput(attrs={"type": "date"}),
        }


class CatalogoJuegosView(LoginRequiredMixin, View):
    """Lista los videojuegos disponibles en el catálogo."""

    def get(self, request):
        juegos = Videojuego.objects.filter(disponible=True).order_by("nombre")
        return render(
            request,
            "core/catalogo_juegos.html",
            {
                "juegos": juegos,
                "tiene_suscripcion": usuario_tiene_suscripcion_activa(request.user),
            },
        )


class JugarView(LoginRequiredMixin, View):
    """Ejecuta el juego HTML5 si el usuario está habilitado."""

    def get(self, request, juego_id):
        juego = get_object_or_404(Videojuego, id=juego_id, disponible=True)

        if juego.requiere_suscripcion and not usuario_tiene_suscripcion_activa(request.user):
            messages.warning(
                request,
                "Necesitas una suscripción activa para jugar a "
                f"'{juego.nombre}'. Elige un plan para continuar.",
            )
            return redirect("suscripcion_form")

        return render(request, "core/jugar.html", {"juego": juego})


class StaffRequiredMixin(UserPassesTestMixin):
    """Restringe el acceso a usuarios staff/admin."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Solo el personal autorizado puede crear videojuegos.",
        )
        return redirect("catalogo_juegos")


class CrearJuegoView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Permite a usuarios staff crear nuevos videojuegos."""

    model = Videojuego
    form_class = VideojuegoForm
    template_name = "core/juego_form.html"
    success_url = reverse_lazy("catalogo_juegos")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(
            self.request,
            f"Videojuego '{form.instance.nombre}' creado correctamente.",
        )
        return respuesta
