from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class TipoSuscripcion(models.TextChoices):
    """Tipos de suscripción disponibles"""
    NORMAL = 'NORMAL', 'Normal'
    PREMIUM = 'PREMIUM', 'Premium'
    VIP = 'VIP', 'VIP'


class EstadoSuscripcion(models.TextChoices):
    """Estados del ciclo de vida de una suscripción"""
    ACTIVA = 'ACTIVA', 'Activa'
    PENDIENTE_RENOVACION = 'PENDIENTE_RENOVACION', 'Pendiente de Renovación'
    CANCELADA = 'CANCELADA', 'Cancelada'
    EXPIRADA = 'EXPIRADA', 'Expirada'


class Juego(models.Model):
    """Representa un videojuego disponible en el catálogo"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100)
    requisitos_minimos = models.TextField()
    disponible = models.BooleanField(default=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Juegos"
    
    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    """
    Representa la suscripción de un usuario al servicio.
    Contiene las reglas de negocio principales del sistema.
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='suscripcion')
    tipo_suscripcion = models.CharField(
        max_length=20,
        choices=TipoSuscripcion.choices,
        default=TipoSuscripcion.NORMAL
    )
    estado = models.CharField(
        max_length=30,
        choices=EstadoSuscripcion.choices,
        default=EstadoSuscripcion.ACTIVA
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_renovacion = models.DateTimeField()
    juegos_seleccionados = models.ManyToManyField(
        Juego,
        related_name='suscripciones',
        blank=True
    )
    notificacion_enviada = models.BooleanField(default=False)
    cambios_mes_actual = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Suscripciones"
    
    def __str__(self):
        return f"Suscripción {self.tipo_suscripcion} - {self.usuario.username}"
    
    # Responsabilidades del dominio
    
    def puede_acceder(self, juego):
        """
        Valida si el usuario puede acceder a un juego según su tipo de suscripción.
        Esta es una regla de negocio core del sistema.
        """
        if self.estado != EstadoSuscripcion.ACTIVA:
            return False
        
        # VIP tiene acceso a todo el catálogo
        if self.tipo_suscripcion == TipoSuscripcion.VIP:
            return juego.disponible
        
        # Normal y Premium solo a juegos seleccionados
        return self.juegos_seleccionados.filter(id=juego.id).exists()
    
    def obtener_limite_juegos(self):
        """Retorna el límite de juegos según el tipo de suscripción"""
        limites = {
            TipoSuscripcion.NORMAL: 3,
            TipoSuscripcion.PREMIUM: 5,
            TipoSuscripcion.VIP: float('inf')  # Sin límite
        }
        return limites.get(self.tipo_suscripcion, 0)
    
    def puede_cambiar_juegos(self):
        """
        Valida si el usuario puede cambiar sus juegos seleccionados.
        Premium y VIP pueden cambiar mensualmente.
        """
        if self.tipo_suscripcion == TipoSuscripcion.NORMAL:
            return self.cambios_mes_actual == 0  # Solo una vez al mes
        
        # Premium y VIP pueden cambiar libremente
        return True
    
    def dias_hasta_renovacion(self):
        """Calcula los días restantes hasta la renovación"""
        delta = self.fecha_renovacion - timezone.now()
        return max(0, delta.days)
    
    def requiere_notificacion(self):
        """Determina si debe notificarse al usuario sobre la renovación"""
        dias_restantes = self.dias_hasta_renovacion()
        return dias_restantes <= 7 and not self.notificacion_enviada
    
    def marcar_para_renovacion(self):
        """Cambia el estado a pendiente de renovación"""
        self.estado = EstadoSuscripcion.PENDIENTE_RENOVACION
        self.save()
    
    def renovar(self, nuevo_tipo=None):
        """
        Renueva la suscripción, opcionalmente cambiando el tipo de plan.
        Reinicia el contador de cambios mensuales.
        """
        if nuevo_tipo and nuevo_tipo in [choice[0] for choice in TipoSuscripcion.choices]:
            self.tipo_suscripcion = nuevo_tipo
        
        self.fecha_renovacion = timezone.now() + timedelta(days=30)
        self.estado = EstadoSuscripcion.ACTIVA
        self.notificacion_enviada = False
        self.cambios_mes_actual = 0
        self.save()
    
    def cancelar(self):
        """Cancela la suscripción"""
        self.estado = EstadoSuscripcion.CANCELADA
        self.save()


class HistorialCambioSuscripcion(models.Model):
    """Auditoría de cambios en las suscripciones"""
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name='historial')
    tipo_anterior = models.CharField(max_length=20, choices=TipoSuscripcion.choices)
    tipo_nuevo = models.CharField(max_length=20, choices=TipoSuscripcion.choices)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Historial de Cambios"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.tipo_anterior} → {self.tipo_nuevo} ({self.fecha_cambio})"


class Pago(models.Model):
    """Representa un pago realizado por el usuario"""
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, default='PENDIENTE')
    referencia = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Pagos"
    
    def validar(self):
        """Valida el pago con el procesador externo"""
        # Aquí iría la lógica de validación real
        self.estado = 'APROBADO'
        self.save()
        return True
    
    def __str__(self):
        return f"Pago {self.referencia} - ${self.monto}"
