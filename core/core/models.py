from django.conf import settings
from django.db import models


class Videojuego(models.Model):
    """Modelo para los videojuegos disponibles en la plataforma"""

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    genero = models.CharField(max_length=100)
    imagen_url = models.URLField(blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    disponible = models.BooleanField(default=True)
    fecha_lanzamiento = models.DateField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-creado_en']


class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    duracion_dias = models.PositiveIntegerField()
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='suscripciones_activas')
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    activa = models.BooleanField(default=True)
    renovacion_automatica = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"

    class Meta:
        ordering = ['-inicio']


class Transaccion(models.Model):
    """Modelo para registrar todas las transacciones de pago"""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('fallida', 'Fallida'),
        ('cancelada', 'Cancelada'),
    ]

    TIPO_CHOICES = [
        ('suscripcion', 'Suscripcion'),
        ('compra_juego', 'Compra de Juego'),
        ('reembolso', 'Reembolso'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transacciones')
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones')
    videojuego = models.ForeignKey(Videojuego, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    referencia_externa = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.monto} - {self.estado}"

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = "Transacciones"