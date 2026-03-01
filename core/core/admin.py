from django.contrib import admin

from .models import Videojuego, Plan, Suscripcion, Transaccion


@admin.register(Videojuego)
class VideojuegoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "genero", "disponible", "creado_en")
    list_filter = ("disponible", "genero", "creado_en")
    search_fields = ("nombre", "descripcion")
    readonly_fields = ("creado_en",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "duracion_dias", "precio_mensual", "activo")
    list_filter = ("activo", "creado_en")
    search_fields = ("nombre",)
    readonly_fields = ("creado_en",)


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "inicio", "fin", "activa", "renovacion_automatica")
    list_filter = ("activa", "plan", "renovacion_automatica")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user", "plan")
    readonly_fields = ("inicio", "fin")


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("user", "monto", "tipo", "estado", "fecha_creacion")
    list_filter = ("tipo", "estado", "fecha_creacion")
    search_fields = ("user__username", "referencia_externa")
    raw_id_fields = ("user", "suscripcion", "videojuego")
    readonly_fields = ("fecha_creacion",)