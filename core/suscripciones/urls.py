from django.urls import path
from .views import (
    CrearSuscripcionView,
    CambiarPlanView,
    CambiarJuegosView,
    VerificarAccesoJuegoView,
    RenovarSuscripcionView,
    ObtenerDetallesSuscripcionView,
    ListarJuegosDisponiblesView
)

app_name = 'suscripciones'

urlpatterns = [
    # Gestión de suscripciones
    path('crear/', CrearSuscripcionView.as_view(), name='crear_suscripcion'),
    path('detalles/', ObtenerDetallesSuscripcionView.as_view(), name='detalles_suscripcion'),
    path('cambiar-plan/', CambiarPlanView.as_view(), name='cambiar_plan'),
    path('cambiar-juegos/', CambiarJuegosView.as_view(), name='cambiar_juegos'),
    path('renovar/', RenovarSuscripcionView.as_view(), name='renovar_suscripcion'),
    
    # Verificación de acceso
    path('verificar-acceso/<int:juego_id>/', VerificarAccesoJuegoView.as_view(), name='verificar_acceso'),
    
    # Catálogo de juegos
    path('juegos/', ListarJuegosDisponiblesView.as_view(), name='listar_juegos'),
]