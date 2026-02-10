from django.test import TestCase
from django.contrib.auth.models import User
from .models import Suscripcion, TipoSuscripcion, EstadoSuscripcion, Juego
from .services import SuscripcionService
from .builders import SuscripcionBuilder, DirectorSuscripcion
from decimal import Decimal


class SuscripcionBuilderTest(TestCase):
    """Tests del patrón Builder"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.builder = SuscripcionBuilder()
        self.juego1 = Juego.objects.create(nombre='FIFA 24', categoria='Deportes')
        self.juego2 = Juego.objects.create(nombre='Call of Duty', categoria='Acción')
    
    def test_builder_construccion_basica(self):
        """Test: El Builder construye una suscripción válida"""
        suscripcion = (self.builder
                      .crear_nueva(self.usuario)
                      .con_tipo(TipoSuscripcion.NORMAL)
                      .con_duracion_dias(30)
                      .activar()
                      .construir())
        
        self.assertIsNotNone(suscripcion.id)
        self.assertEqual(suscripcion.tipo_suscripcion, TipoSuscripcion.NORMAL)
        self.assertEqual(suscripcion.estado, EstadoSuscripcion.ACTIVA)
    
    def test_builder_validacion_limite_juegos(self):
        """Test: El Builder valida el límite de juegos según el plan"""
        # Crear 4 juegos para exceder el límite de Normal (3)
        juegos = [self.juego1, self.juego2,
                 Juego.objects.create(nombre='GTA V', categoria='Acción'),
                 Juego.objects.create(nombre='Minecraft', categoria='Aventura')]
        
        # Intentar crear suscripción Normal con 4 juegos (debería fallar)
        builder = SuscripcionBuilder()
        builder.crear_nueva(self.usuario)
        builder.con_tipo(TipoSuscripcion.NORMAL)
        builder.con_duracion_dias(30)
        builder.con_juegos_seleccionados(juegos)
        
        self.assertFalse(builder.validar())
        errores = builder.obtener_errores()
        self.assertTrue(any('permite máximo 3' in e for e in errores))
    
    def test_director_suscripcion_premium(self):
        """Test: El Director crea suscripciones Premium correctamente"""
        director = DirectorSuscripcion(SuscripcionBuilder())
        juegos = [self.juego1, self.juego2]
        
        suscripcion = director.construir_suscripcion_premium(self.usuario, juegos)
        
        self.assertEqual(suscripcion.tipo_suscripcion, TipoSuscripcion.PREMIUM)
        self.assertEqual(suscripcion.juegos_seleccionados.count(), 2)
        self.assertEqual(suscripcion.estado, EstadoSuscripcion.ACTIVA)


class SuscripcionServiceTest(TestCase):
    """Tests de la capa de servicios"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='serviceuser',
            email='service@test.com',
            password='testpass123'
        )
        self.servicio = SuscripcionService()
        
        # Crear juegos de prueba
        self.juegos = [
            Juego.objects.create(nombre=f'Juego {i}', categoria='Test')
            for i in range(1, 6)
        ]
    
    def test_crear_suscripcion_normal(self):
        """Test: El servicio crea una suscripción Normal"""
        juegos_ids = [j.id for j in self.juegos[:3]]
        
        suscripcion, errores = self.servicio.crear_suscripcion(
            usuario=self.usuario,
            tipo_suscripcion=TipoSuscripcion.NORMAL,
            juegos_ids=juegos_ids
        )
        
        self.assertEqual(len(errores), 0)
        self.assertIsNotNone(suscripcion)
        self.assertEqual(suscripcion.tipo_suscripcion, TipoSuscripcion.NORMAL)
        self.assertEqual(suscripcion.juegos_seleccionados.count(), 3)
    
    def test_verificar_acceso_juego_vip(self):
        """Test: VIP tiene acceso a todos los juegos"""
        # Crear suscripción VIP
        suscripcion, _ = self.servicio.crear_suscripcion(
            usuario=self.usuario,
            tipo_suscripcion=TipoSuscripcion.VIP
        )
        
        # Verificar acceso a cualquier juego
        resultado = self.servicio.verificar_acceso_juego(
            suscripcion_id=suscripcion.id,
            juego_id=self.juegos[0].id
        )
        
        self.assertTrue(resultado['tiene_acceso'])
    
    def test_verificar_acceso_juego_normal_sin_seleccion(self):
        """Test: Normal sin seleccionar el juego no tiene acceso"""
        # Crear suscripción Normal con juegos específicos
        juegos_ids = [self.juegos[0].id, self.juegos[1].id]
        suscripcion, _ = self.servicio.crear_suscripcion(
            usuario=self.usuario,
            tipo_suscripcion=TipoSuscripcion.NORMAL,
            juegos_ids=juegos_ids
        )
        
        # Intentar acceder a un juego NO seleccionado
        resultado = self.servicio.verificar_acceso_juego(
            suscripcion_id=suscripcion.id,
            juego_id=self.juegos[2].id  # Juego no seleccionado
        )
        
        self.assertFalse(resultado['tiene_acceso'])
    
    def test_cambiar_plan_de_normal_a_premium(self):
        """Test: Cambio de plan Normal a Premium"""
        # Crear suscripción Normal
        suscripcion, _ = self.servicio.crear_suscripcion(
            usuario=self.usuario,
            tipo_suscripcion=TipoSuscripcion.NORMAL,
            juegos_ids=[self.juegos[0].id]
        )
        
        # Cambiar a Premium
        resultado = self.servicio.cambiar_plan(
            suscripcion_id=suscripcion.id,
            nuevo_tipo=TipoSuscripcion.PREMIUM,
            procesar_pago=False  # Desactivar pago para test
        )
        
        self.assertTrue(resultado['exito'])
        self.assertEqual(resultado['tipo_nuevo'], TipoSuscripcion.PREMIUM)
        
        # Verificar que se actualizó
        suscripcion.refresh_from_db()
        self.assertEqual(suscripcion.tipo_suscripcion, TipoSuscripcion.PREMIUM)
    
    def test_cambiar_juegos_respeta_limite(self):
        """Test: No se puede exceder el límite de juegos al cambiar"""
        # Crear suscripción Normal (máximo 3 juegos)
        suscripcion, _ = self.servicio.crear_suscripcion(
            usuario=self.usuario,
            tipo_suscripcion=TipoSuscripcion.NORMAL,
            juegos_ids=[self.juegos[0].id]
        )
        
        # Intentar cambiar a 4 juegos (debería fallar)
        juegos_ids = [j.id for j in self.juegos[:4]]
        resultado = self.servicio.cambiar_juegos_seleccionados(
            suscripcion_id=suscripcion.id,
            nuevos_juegos_ids=juegos_ids
        )
        
        self.assertFalse(resultado['exito'])
        self.assertIn('permite máximo 3', resultado['error'])


class RegrasDeNegocioTest(TestCase):
    """Tests de las reglas de negocio del dominio"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='businessuser',
            email='business@test.com',
            password='testpass123'
        )
        self.juego_disponible = Juego.objects.create(
            nombre='Disponible',
            categoria='Test',
            disponible=True
        )
        self.juego_no_disponible = Juego.objects.create(
            nombre='No Disponible',
            categoria='Test',
            disponible=False
        )
    
    def test_regla_vip_acceso_completo(self):
        """Test: VIP accede a todo el catálogo"""
        builder = SuscripcionBuilder()
        suscripcion = (builder
                      .crear_nueva(self.usuario)
                      .con_tipo(TipoSuscripcion.VIP)
                      .con_duracion_dias(30)
                      .activar()
                      .construir())
        
        # Puede acceder a cualquier juego disponible
        self.assertTrue(suscripcion.puede_acceder(self.juego_disponible))
        
        # No puede acceder a juegos no disponibles
        self.assertFalse(suscripcion.puede_acceder(self.juego_no_disponible))
    
    def test_regla_normal_solo_seleccionados(self):
        """Test: Normal solo accede a juegos seleccionados"""
        builder = SuscripcionBuilder()
        suscripcion = (builder
                      .crear_nueva(self.usuario)
                      .con_tipo(TipoSuscripcion.NORMAL)
                      .con_duracion_dias(30)
                      .con_juegos_seleccionados([self.juego_disponible])
                      .activar()
                      .construir())
        
        # Puede acceder al juego seleccionado
        self.assertTrue(suscripcion.puede_acceder(self.juego_disponible))
    
    def test_regla_limite_juegos_por_plan(self):
        """Test: Cada plan tiene un límite diferente de juegos"""
        # Normal: 3 juegos
        suscripcion_normal = Suscripcion(tipo_suscripcion=TipoSuscripcion.NORMAL)
        self.assertEqual(suscripcion_normal.obtener_limite_juegos(), 3)
        
        # Premium: 5 juegos
        suscripcion_premium = Suscripcion(tipo_suscripcion=TipoSuscripcion.PREMIUM)
        self.assertEqual(suscripcion_premium.obtener_limite_juegos(), 5)
        
        # VIP: ilimitado
        suscripcion_vip = Suscripcion(tipo_suscripcion=TipoSuscripcion.VIP)
        self.assertEqual(suscripcion_vip.obtener_limite_juegos(), float('inf'))
