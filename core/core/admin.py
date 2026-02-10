from django.contrib import admin

from .models import Plan, Suscripcion


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "duracion_dias", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "inicio", "fin", "activa")
    list_filter = ("activa", "plan")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user", "plan")