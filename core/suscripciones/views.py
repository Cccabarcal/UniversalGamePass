from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services import SuscripcionService
from .models import Juego
import json


@method_decorator(csrf_exempt, name='dispatch')
class CrearSuscripcionView(LoginRequiredMixin, View):
    """
    Vista para crear una nueva suscripción.
    Su única responsabilidad es capturar los datos del request y llamar al servicio.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicio = SuscripcionService()
    
    def post(self, request):
        """
        POST /suscripciones/crear/
        Body: {
            "tipo_suscripcion": "PREMIUM",
            "juegos_ids": [1, 2, 3]
        }
        """
        try:
            # 1. Capturar datos del request
            data = json.loads(request.body)
            tipo_suscripcion = data.get('tipo_suscripcion')
            juegos_ids = data.get('juegos_ids', [])
            
            # 2. Llamar al servicio (NO hay lógica de negocio aquí)
            suscripcion, errores = self.servicio.crear_suscripcion(
                usuario=request.user,
                tipo_suscripcion=tipo_suscripcion,
                juegos_ids=juegos_ids
            )
            
            # 3. Retornar respuesta
            if errores:
                return JsonResponse({
                    'exito': False,
                    'errores': errores
                }, status=400)
            
            return JsonResponse({
                'exito': True,
                'suscripcion': {
                    'id': suscripcion.id,
                    'tipo': suscripcion.tipo_suscripcion,
                    'estado': suscripcion.estado,
                    'fecha_renovacion': suscripcion.fecha_renovacion.isoformat(),
                    'juegos_seleccionados': [
                        {'id': j.id, 'nombre': j.nombre} 
                        for j in suscripcion.juegos_seleccionados.all()
                    ]
                }
            }, status=201)
            
        except ValueError as e:
            return JsonResponse({
                'exito': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'exito': False,
                'error': 'Error interno del servidor'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CambiarPlanView(LoginRequiredMixin, View):
    """
    Vista para cambiar el plan de suscripción.
    Delega toda la lógica al servicio.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicio = SuscripcionService()
    
    def post(self, request):
        """
        POST /suscripciones/cambiar-plan/
        Body: {
            "nuevo_tipo": "VIP",
            "procesar_pago": true
        }
        """
        try:
            # 1. Capturar datos
            data = json.loads(request.body)
            nuevo_tipo = data.get('nuevo_tipo')
            procesar_pago = data.get('procesar_pago', True)
            
            # 2. Obtener suscripción del usuario
            suscripcion_id = request.user.suscripcion.id
            
            # 3. Llamar al servicio
            resultado = self.servicio.cambiar_plan(
                suscripcion_id=suscripcion_id,
                nuevo_tipo=nuevo_tipo,
                procesar_pago=procesar_pago
            )
            
            # 4. Retornar respuesta
            if not resultado['exito']:
                return JsonResponse(resultado, status=400)
            
            return JsonResponse(resultado, status=200)
            
        except Exception as e:
            return JsonResponse({
                'exito': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CambiarJuegosView(LoginRequiredMixin, View):
    """
    Vista para cambiar los juegos seleccionados.
    Sin lógica de negocio, solo coordina con el servicio.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicio = SuscripcionService()
    
    def post(self, request):
        """
        POST /suscripciones/cambiar-juegos/
        Body: {
            "juegos_ids": [5, 6, 7]
        }
        """
        try:
            # 1. Capturar datos
            data = json.loads(request.body)
            juegos_ids = data.get('juegos_ids', [])
            
            # 2. Obtener suscripción
            suscripcion_id = request.user.suscripcion.id
            
            # 3. Llamar al servicio
            resultado = self.servicio.cambiar_juegos_seleccionados(
                suscripcion_id=suscripcion_id,
                nuevos_juegos_ids=juegos_ids
            )
            
            # 4. Retornar respuesta
            if not resultado['exito']:
                return JsonResponse(resultado, status=400)
            
            return JsonResponse(resultado, status=200)
            
        except Exception as e:
            return JsonResponse({
                'exito': False,
                'error': str(e)
            }, status=500)


class VerificarAccesoJuegoView(LoginRequiredMixin, View):
    """
    Vista para verificar si el usuario tiene acceso a un juego.
    Esta es una de las funcionalidades core del sistema.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicio = SuscripcionService()
    
    def get(self, request, juego_id):
        """
        GET /suscripciones/verificar-acceso/<juego_id>/
        """
        try:
            # 1. Capturar datos
            suscripcion_id = request.user.suscripcion.id
            
            # 2. Llamar al servicio
            resultado = self.servicio.verificar_acceso_juego(
                suscripcion_id=suscripcion_id,
                juego_id=juego_id
            )
            
            # 3. Retornar respuesta
            return JsonResponse(resultado, status=200)
            
        except AttributeError:
            return JsonResponse({
                'tiene_acceso': False,
                'motivo': 'No tienes una suscripción activa'
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'tiene_acceso': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RenovarSuscripcionView(LoginRequiredMixin, View):
    """
    Vista para renovar una suscripción.
    Procesa el pago y actualiza la suscripción.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servicio = SuscripcionService()
    
    def post(self, request):
        """
        POST /suscripciones/renovar/
        Body: {
            "nuevo_tipo": "PREMIUM",  // Opcional
            "metodo_pago": "stripe"
        }
        """
        try:
            # 1. Capturar datos
            data = json.loads(request.body)
            nuevo_tipo = data.get('nuevo_tipo')
            metodo_pago = data.get('metodo_pago', 'stripe')
            
            # 2. Obtener suscripción
            suscripcion_id = request.user.suscripcion.id
            
            # 3. Llamar al servicio
            resultado = self.servicio.renovar_suscripcion(
                suscripcion_id=suscripcion_id,
                nuevo_tipo=nuevo_tipo,
                metodo_pago=metodo_pago
            )
            
            # 4. Retornar respuesta
            if not resultado['exito']:
                return JsonResponse(resultado, status=400)
            
            return JsonResponse(resultado, status=200)
            
        except Exception as e:
            return JsonResponse({
                'exito': False,
                'error': str(e)
            }, status=500)


class ObtenerDetallesSuscripcionView(LoginRequiredMixin, View):
    """
    Vista para obtener los detalles de la suscripción del usuario.
    """
    
    def get(self, request):
        """
        GET /suscripciones/detalles/
        """
        try:
            suscripcion = request.user.suscripcion
            
            return JsonResponse({
                'id': suscripcion.id,
                'tipo': suscripcion.tipo_suscripcion,
                'estado': suscripcion.estado,
                'fecha_inicio': suscripcion.fecha_inicio.isoformat(),
                'fecha_renovacion': suscripcion.fecha_renovacion.isoformat(),
                'dias_hasta_renovacion': suscripcion.dias_hasta_renovacion(),
                'limite_juegos': suscripcion.obtener_limite_juegos(),
                'juegos_seleccionados': [
                    {
                        'id': j.id,
                        'nombre': j.nombre,
                        'categoria': j.categoria
                    }
                    for j in suscripcion.juegos_seleccionados.all()
                ],
                'puede_cambiar_juegos': suscripcion.puede_cambiar_juegos(),
                'cambios_realizados_mes': suscripcion.cambios_mes_actual
            }, status=200)
            
        except AttributeError:
            return JsonResponse({
                'error': 'No tienes una suscripción activa'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class ListarJuegosDisponiblesView(View):
    """
    Vista para listar todos los juegos disponibles en el catálogo.
    """
    
    def get(self, request):
        """
        GET /juegos/
        """
        try:
            juegos = Juego.objects.filter(disponible=True)
            
            return JsonResponse({
                'juegos': [
                    {
                        'id': j.id,
                        'nombre': j.nombre,
                        'descripcion': j.descripcion,
                        'categoria': j.categoria
                    }
                    for j in juegos
                ]
            }, status=200)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)