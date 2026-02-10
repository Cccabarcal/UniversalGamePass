from django.contrib import admin
from .models import Suscripcion, Juego, Pago, HistorialCambioSuscripcion


@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'disponible', 'fecha_agregado']
    list_filter = ['categoria', 'disponible']
    search_fields = ['nombre', 'descripcion']


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_suscripcion', 'estado', 'fecha_renovacion', 'dias_restantes']
    list_filter = ['tipo_suscripcion', 'estado']
    search_fields = ['usuario__username', 'usuario__email']
    filter_horizontal = ['juegos_seleccionados']
    
    def dias_restantes(self, obj):
        return obj.dias_hasta_renovacion()
    dias_restantes.short_description = 'Días hasta renovación'


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['referencia', 'suscripcion', 'monto', 'estado', 'fecha_pago']
    list_filter = ['estado', 'metodo_pago']
    search_fields = ['referencia', 'suscripcion__usuario__username']


@admin.register(HistorialCambioSuscripcion)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ['suscripcion', 'tipo_anterior', 'tipo_nuevo', 'fecha_cambio']
    list_filter = ['tipo_anterior', 'tipo_nuevo']
    search_fields = ['suscripcion__usuario__username']