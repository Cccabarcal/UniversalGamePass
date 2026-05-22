"""
URL configuration for core project.
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from .views import (
    CrearSuscripcionView,
    CancelarSuscripcionView,
    SuscripcionFormView,
    HomeView,
    SignUpView,
    ProfileView,
    CatalogoJuegosView,
    RAWGHubView,
    JugarView,
    CrearJuegoView,
    SistemaInfoAPI,
    AliadoInfoAPI,
    AliadoInfoView,
    TerceraAPIView,
)
from .views.api import (
    PlanListAPI, PlanDetailAPI,
    VideojuegoListAPI, VideojuegoDetailAPI,
    SuscripcionListAPI, SuscripcionCreateAPI, SuscripcionDetailAPI,
    TransaccionListAPI, TransaccionDetailAPI, TransaccionEstadisticasAPI,
)

urlpatterns = [
    # Web Views
    path("", HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("accounts/logout/", LogoutView.as_view(next_page="home", http_method_names=['get', 'post']), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("suscripciones/nueva/", SuscripcionFormView.as_view(), name="suscripcion_form"),
    path("suscripciones/crear/", CrearSuscripcionView.as_view(), name="crear_suscripcion"),
    path("suscripciones/cancelar/", CancelarSuscripcionView.as_view(), name="cancelar_suscripcion"),

    # Catalogo de videojuegos
    path("juegos/", CatalogoJuegosView.as_view(), name="catalogo_juegos"),
    path("rawg-hub/", RAWGHubView.as_view(), name="rawg_hub"),
    path("juegos/crear/", CrearJuegoView.as_view(), name="crear_juego"),
    path("juegos/<int:juego_id>/jugar/", JugarView.as_view(), name="jugar_juego"),

    # Integraciones (Adapter, aliado, info del sistema) - HTML
    path("integraciones/aliado/", AliadoInfoView.as_view(), name="aliado_info"),
    path("integraciones/terceros/", TerceraAPIView.as_view(), name="terceros_info"),

    # API REST v1 (incluye Servicio a Proveer y consumo de aliado)
    path("api/v1/sistema/info/", SistemaInfoAPI.as_view(), name="api_sistema_info"),
    path("api/v1/aliado/info/", AliadoInfoAPI.as_view(), name="api_aliado_info"),
    path("api/v1/planes/", PlanListAPI.as_view(), name="api_planes_list"),
    path("api/v1/planes/<int:plan_id>/", PlanDetailAPI.as_view(), name="api_planes_detail"),
    path("api/v1/videojuegos/", VideojuegoListAPI.as_view(), name="api_videojuegos_list"),
    path("api/v1/videojuegos/<int:videojuego_id>/", VideojuegoDetailAPI.as_view(), name="api_videojuegos_detail"),
    path("api/v1/suscripciones/", SuscripcionListAPI.as_view(), name="api_suscripciones_list"),
    path("api/v1/suscripciones/crear/", SuscripcionCreateAPI.as_view(), name="api_suscripciones_crear"),
    path("api/v1/suscripciones/<int:suscripcion_id>/", SuscripcionDetailAPI.as_view(), name="api_suscripciones_detail"),
    path("api/v1/transacciones/", TransaccionListAPI.as_view(), name="api_transacciones_list"),
    path("api/v1/transacciones/<int:transaccion_id>/", TransaccionDetailAPI.as_view(), name="api_transacciones_detail"),
    path("api/v1/transacciones/estadisticas/", TransaccionEstadisticasAPI.as_view(), name="api_transacciones_estadisticas"),

    # Aliases de compatibilidad (rutas viejas /api/...)
    path("api/planes/", PlanListAPI.as_view()),
    path("api/planes/<int:plan_id>/", PlanDetailAPI.as_view()),
    path("api/videojuegos/", VideojuegoListAPI.as_view()),
    path("api/videojuegos/<int:videojuego_id>/", VideojuegoDetailAPI.as_view()),
    path("api/suscripciones/", SuscripcionListAPI.as_view()),
    path("api/suscripciones/crear/", SuscripcionCreateAPI.as_view()),
    path("api/suscripciones/<int:suscripcion_id>/", SuscripcionDetailAPI.as_view()),
    path("api/transacciones/", TransaccionListAPI.as_view()),
    path("api/transacciones/<int:transaccion_id>/", TransaccionDetailAPI.as_view()),
    path("api/transacciones/estadisticas/", TransaccionEstadisticasAPI.as_view()),
]
