from django.conf import settings
from django.db import models


class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    duracion_dias = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"