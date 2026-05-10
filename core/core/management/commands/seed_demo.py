"""
Comando: python manage.py seed_demo

Crea datos de demostracion: Planes, Videojuegos y un usuario admin.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Plan, Videojuego


PLANES = [
    {
        "nombre": "Basico",
        "duracion_dias": 30,
        "precio_mensual": 9.99,
        "descripcion": "Acceso al catalogo principal por 30 dias.",
        "activo": True,
    },
    {
        "nombre": "Pro",
        "duracion_dias": 90,
        "precio_mensual": 24.99,
        "descripcion": "3 meses de acceso completo con prioridad.",
        "activo": True,
    },
    {
        "nombre": "Premium",
        "duracion_dias": 365,
        "precio_mensual": 79.99,
        "descripcion": "Un ano completo con todos los beneficios.",
        "activo": True,
    },
    # === 3 nuevos planes ===
    {
        "nombre": "Indie",
        "duracion_dias": 15,
        "precio_mensual": 4.99,
        "descripcion": "Plan ligero de 15 dias, ideal para probar la plataforma.",
        "activo": True,
    },
    {
        "nombre": "Familia",
        "duracion_dias": 60,
        "precio_mensual": 19.99,
        "descripcion": "Plan compartido para hasta 4 miembros del hogar (60 dias).",
        "activo": True,
    },
    {
        "nombre": "Anual Premium",
        "duracion_dias": 365,
        "precio_mensual": 129.99,
        "descripcion": "Acceso completo durante 1 ano con beneficios exclusivos y soporte prioritario.",
        "activo": True,
    },
]


JUEGOS = [
    {
        "nombre": "Snake Classic",
        "descripcion": "El clasico juego de la serpiente. Come la comida y crece sin chocarte.",
        "genero": "Arcade",
        "slug_ejecutable": "snake",
        "requiere_suscripcion": True,
        "disponible": True,
    },
    {
        "nombre": "Block Drop",
        "descripcion": "Juego de bloques al estilo Tetris. Completa filas para sumar puntos.",
        "genero": "Puzzle",
        "slug_ejecutable": "tetris",
        "requiere_suscripcion": True,
        "disponible": True,
    },
    {
        "nombre": "Pong Arena",
        "descripcion": "Reta a la CPU en un duelo clasico de pong. Primero a 5 puntos gana.",
        "genero": "Deportes",
        "slug_ejecutable": "pong",
        "requiere_suscripcion": True,
        "disponible": True,
    },
    {
        "nombre": "Brick Breaker",
        "descripcion": "Rompe todos los ladrillos con la pelota antes de quedarte sin vidas.",
        "genero": "Arcade",
        "slug_ejecutable": "breakout",
        "requiere_suscripcion": False,
        "disponible": True,
    },
]


class Command(BaseCommand):
    help = "Crea planes y videojuegos de demostracion."

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("== Seed de planes =="))
        for data in PLANES:
            plan, creado = Plan.objects.get_or_create(
                nombre=data["nombre"], defaults=data
            )
            estado = "creado" if creado else "ya existia"
            self.stdout.write(f"  - Plan {plan.nombre} ({estado})")

        self.stdout.write(self.style.HTTP_INFO("== Seed de videojuegos =="))
        for data in JUEGOS:
            juego, creado = Videojuego.objects.get_or_create(
                nombre=data["nombre"], defaults=data
            )
            estado = "creado" if creado else "ya existia"
            self.stdout.write(f"  - {juego.nombre} ({estado})")

        self.stdout.write(self.style.HTTP_INFO("== Usuario admin demo =="))
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@ugp.local", password="admin12345"
            )
            self.stdout.write("  - Usuario admin creado (admin / admin12345)")
        else:
            self.stdout.write("  - Usuario admin ya existia")

        self.stdout.write(self.style.SUCCESS("Seed completado."))
