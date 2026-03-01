"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    CrearSuscripcionView,
    SuscripcionFormView,
    HomeView,
    SignUpView,
    ProfileView,
    PlanListAPIView,
    PlanDetailAPIView,
    VideojuegoListAPIView,
    VideojuegoDetailAPIView,
    SuscripcionListAPIView,
    SuscripcionCreateAPIView,
    SuscripcionDetailAPIView,
    TransaccionListAPIView,
    TransaccionDetailAPIView,
)

urlpatterns = [
    # Web Views (Vistas tradicionales)
    path("", HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path("accounts/login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("accounts/logout/", LogoutView.as_view(next_page="home", http_method_names=['get', 'post']), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("suscripciones/nueva/", SuscripcionFormView.as_view(), name="suscripcion_form"),
    path("suscripciones/crear/", CrearSuscripcionView.as_view(), name="crear_suscripcion"),
    
    # API REST Endpoints 
    path("api/planes/", PlanListAPIView.as_view(), name="api_planes_list"),
    path("api/planes/<int:plan_id>/", PlanDetailAPIView.as_view(), name="api_planes_detail"),
    path("api/videojuegos/", VideojuegoListAPIView.as_view(), name="api_videojuegos_list"),
    path("api/videojuegos/<int:videojuego_id>/", VideojuegoDetailAPIView.as_view(), name="api_videojuegos_detail"),
    path("api/suscripciones/", SuscripcionListAPIView.as_view(), name="api_suscripciones_list"),
    path("api/suscripciones/crear/", SuscripcionCreateAPIView.as_view(), name="api_suscripciones_crear"),
    path("api/suscripciones/<int:suscripcion_id>/", SuscripcionDetailAPIView.as_view(), name="api_suscripciones_detail"),
    path("api/transacciones/", TransaccionListAPIView.as_view(), name="api_transacciones_list"),
    path("api/transacciones/<int:transaccion_id>/", TransaccionDetailAPIView.as_view(), name="api_transacciones_detail"),
]

