from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .infra.factories import NotificadorFactory
from .models import Plan
from .services import SuscripcionService


class SuscripcionFormView(LoginRequiredMixin, View):
    def get(self, request):
        planes = Plan.objects.filter(activo=True).order_by("nombre")
        return render(request, "core/suscripcion_form.html", {"planes": planes})


class CrearSuscripcionView(LoginRequiredMixin, View):
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