from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from suscripciones.models import Juego, TipoSuscripcion
from suscripciones.services import SuscripcionService


class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el sistema de suscripciones'

    def handle(self, *args, **kwargs):
        # Crear juegos
        juegos_data = [
            ('Cyberpunk 2077', 'RPG', 'RPG futurista de mundo abierto'),
            ('FIFA 24', 'Deportes', 'Simulador de fútbol'),
            ('Call of Duty MW', 'Acción', 'Shooter en primera persona'),
            ('The Witcher 3', 'RPG', 'Fantasía medieval'),
            ('Forza Horizon 5', 'Carreras', 'Carreras mundo abierto'),
            ('Elden Ring', 'RPG', 'Souls-like de fantasía'),
            ('GTA V', 'Acción', 'Acción y aventura'),
            ('Minecraft', 'Aventura', 'Sandbox creativo'),
        ]
        
        for nombre, categoria, desc in juegos_data:
            Juego.objects.get_or_create(
                nombre=nombre,
                defaults={'categoria': categoria, 'descripcion': desc}
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ {len(juegos_data)} juegos creados'))
        
        # Crear usuarios de ejemplo
        usuarios = [
            ('maria', 'maria@test.com', TipoSuscripcion.PREMIUM),
            ('juan', 'juan@test.com', TipoSuscripcion.NORMAL),
            ('pedro', 'pedro@test.com', TipoSuscripcion.VIP),
        ]
        
        servicio = SuscripcionService()
        juegos = list(Juego.objects.all()[:5])
        
        for username, email, tipo in usuarios:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('password123')
                user.save()
            
            if not hasattr(user, 'suscripcion'):
                suscripcion, _ = servicio.crear_suscripcion(
                    usuario=user,
                    tipo_suscripcion=tipo,
                    juegos_ids=[j.id for j in juegos[:3]]
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Suscripción {tipo} para {username}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Datos de ejemplo cargados!'))