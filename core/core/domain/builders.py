from datetime import timedelta
from django.utils import timezone
from ..models import Suscripcion

class SuscripcionBuilder:
    def para_usuario(self, user):
        if user is None:
            raise ValueError("El usuario es obligatorio")
        self.user = user
        return self

    def con_plan(self, plan):
        if plan is None:
            raise ValueError("El plan es obligatorio")
        if not plan.activo:
            raise ValueError("El plan no está activo")
        self.plan = plan
        return self

    def calcular_vigencia(self):
        if not hasattr(self, "plan"):
            raise ValueError("Debe asignar un plan antes de calcular la vigencia")
        self.inicio = timezone.now()
        self.fin = self.inicio + timedelta(days=self.plan.duracion_dias)
        return self

    def build(self):
        if not hasattr(self, "user"):
            raise ValueError("Debe asignar un usuario antes de construir la suscripción")
        if not hasattr(self, "plan"):
            raise ValueError("Debe asignar un plan antes de construir la suscripción")
        if not hasattr(self, "inicio") or not hasattr(self, "fin"):
            raise ValueError("Debe calcular la vigencia antes de construir la suscripción")
        return Suscripcion.objects.create(
            user=self.user,
            plan=self.plan,
            inicio=self.inicio,
            fin=self.fin,
            activa=True
        )