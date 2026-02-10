from django.db import transaction
from django.utils import timezone
from .models import (
    Suscripcion, TipoSuscripcion, EstadoSuscripcion, 
    HistorialCambioSuscripcion, Pago, Juego
)
from .builders import SuscripcionBuilder, DirectorSuscripcion
from .factories import (
    NotificadorFactory, 
    CalculadorPrecioFactory,
    ProcesadorPagoFactory
)
import uuid


class SuscripcionService:
    """
    Servicio que gestiona toda la lógica de negocio de suscripciones.
    Orquesta el Builder para crear suscripciones y las Factories para
    instanciar dependencias externas (notificadores, calculadores, procesadores).
    
    Esta clase implementa el principio de Single Responsibility:
    solo se encarga de la lógica de negocio de suscripciones.
    """
    
    def __init__(self):
        # Inyección de dependencias mediante Factories
        self.notificador = NotificadorFactory.crear_notificador(tipo='email')
        self.calculador_precio = CalculadorPrecioFactory.crear_calculador(tipo='estandar')
        self.builder = SuscripcionBuilder()
        self.director = DirectorSuscripcion(self.builder)
    
    # ========================================================================
    # CASO DE USO 1: Crear nueva suscripción
    # ========================================================================
    
    @transaction.atomic
    def crear_suscripcion(self, usuario, tipo_suscripcion, juegos_ids=None):
        """
        Crea una nueva suscripción para un usuario.
        
        Args:
            usuario: Instancia de User
            tipo_suscripcion: String con el tipo (NORMAL, PREMIUM, VIP)
            juegos_ids: Lista de IDs de juegos a seleccionar (opcional)
        
        Returns:
            Tupla (suscripcion, errores)
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar que el usuario no tenga ya una suscripción activa
        if hasattr(usuario, 'suscripcion'):
            raise ValueError("El usuario ya tiene una suscripción activa")
        
        # Obtener juegos si se proporcionaron IDs
        juegos = []
        if juegos_ids:
            juegos = list(Juego.objects.filter(id__in=juegos_ids, disponible=True))
        
        try:
            # Usar el Builder para construir la suscripción
            if tipo_suscripcion == TipoSuscripcion.VIP:
                # VIP no necesita juegos seleccionados (acceso a todo)
                suscripcion = self.director.construir_suscripcion_vip(usuario)
            elif tipo_suscripcion == TipoSuscripcion.PREMIUM:
                suscripcion = self.director.construir_suscripcion_premium(usuario, juegos)
            else:  # NORMAL
                suscripcion = self.director.construir_suscripcion_normal(usuario, juegos)
            
            # Registrar en el historial
            HistorialCambioSuscripcion.objects.create(
                suscripcion=suscripcion,
                tipo_anterior='NINGUNO',
                tipo_nuevo=tipo_suscripcion,
                motivo='Suscripción inicial'
            )
            
            return suscripcion, []
            
        except ValueError as e:
            return None, [str(e)]
    
    # ========================================================================
    # CASO DE USO 2: Cambiar plan de suscripción (upgrade/downgrade)
    # ========================================================================
    
    @transaction.atomic
    def cambiar_plan(self, suscripcion_id, nuevo_tipo, procesar_pago=True):
        """
        Cambia el plan de una suscripción existente.
        Calcula el costo prorrateado y procesa el pago si es necesario.
        
        Args:
            suscripcion_id: ID de la suscripción
            nuevo_tipo: Nuevo tipo de suscripción
            procesar_pago: Si debe procesar el pago del upgrade
        
        Returns:
            Dict con el resultado del cambio
        """
        try:
            suscripcion = Suscripcion.objects.get(id=suscripcion_id)
        except Suscripcion.DoesNotExist:
            return {
                'exito': False,
                'error': 'Suscripción no encontrada'
            }
        
        # Validar que la suscripción esté activa
        if suscripcion.estado != EstadoSuscripcion.ACTIVA:
            return {
                'exito': False,
                'error': f'La suscripción está en estado {suscripcion.estado}'
            }
        
        # Validar que sea un cambio real
        tipo_anterior = suscripcion.tipo_suscripcion
        if tipo_anterior == nuevo_tipo:
            return {
                'exito': False,
                'error': 'El plan seleccionado es el mismo que el actual'
            }
        
        # Calcular costo del cambio
        dias_restantes = suscripcion.dias_hasta_renovacion()
        costo_upgrade = self.calculador_precio.calcular_precio_upgrade(
            tipo_anterior,
            nuevo_tipo,
            dias_restantes
        )
        
        resultado = {
            'exito': True,
            'tipo_anterior': tipo_anterior,
            'tipo_nuevo': nuevo_tipo,
            'costo_upgrade': float(costo_upgrade),
            'dias_restantes': dias_restantes,
            'pago_procesado': False
        }
        
        # Si hay costo y se debe procesar el pago
        if costo_upgrade > 0 and procesar_pago:
            pago_resultado = self._procesar_pago_upgrade(
                suscripcion,
                costo_upgrade,
                f"Upgrade de {tipo_anterior} a {nuevo_tipo}"
            )
            
            if not pago_resultado['exito']:
                resultado['exito'] = False
                resultado['error'] = 'Error al procesar el pago'
                return resultado
            
            resultado['pago_procesado'] = True
            resultado['transaccion_id'] = pago_resultado['transaccion_id']
        
        # Actualizar la suscripción
        suscripcion.tipo_suscripcion = nuevo_tipo
        
        # Si cambia de VIP a otro plan, debe seleccionar juegos
        if tipo_anterior == TipoSuscripcion.VIP and nuevo_tipo != TipoSuscripcion.VIP:
            suscripcion.juegos_seleccionados.clear()
            resultado['requiere_seleccion_juegos'] = True
        
        # Si cambia a VIP, puede acceder a todo
        if nuevo_tipo == TipoSuscripcion.VIP:
            suscripcion.juegos_seleccionados.clear()
        
        suscripcion.save()
        
        # Registrar en el historial
        HistorialCambioSuscripcion.objects.create(
            suscripcion=suscripcion,
            tipo_anterior=tipo_anterior,
            tipo_nuevo=nuevo_tipo,
            motivo=f'Cambio de plan (costo: ${costo_upgrade})'
        )
        
        # Notificar al usuario
        self.notificador.notificar_cambio_plan(suscripcion, tipo_anterior, nuevo_tipo)
        
        return resultado
    
    # ========================================================================
    # CASO DE USO 3: Cambiar juegos seleccionados
    # ========================================================================
    
    @transaction.atomic
    def cambiar_juegos_seleccionados(self, suscripcion_id, nuevos_juegos_ids):
        """
        Cambia los juegos seleccionados de una suscripción.
        Valida los límites según el tipo de plan.
        
        Args:
            suscripcion_id: ID de la suscripción
            nuevos_juegos_ids: Lista de IDs de los nuevos juegos
        
        Returns:
            Dict con el resultado
        """
        try:
            suscripcion = Suscripcion.objects.get(id=suscripcion_id)
        except Suscripcion.DoesNotExist:
            return {
                'exito': False,
                'error': 'Suscripción no encontrada'
            }
        
        # VIP tiene acceso a todo, no necesita seleccionar
        if suscripcion.tipo_suscripcion == TipoSuscripcion.VIP:
            return {
                'exito': False,
                'error': 'Las suscripciones VIP tienen acceso a todo el catálogo'
            }
        
        # Validar que pueda cambiar juegos
        if not suscripcion.puede_cambiar_juegos():
            return {
                'exito': False,
                'error': 'Ya se alcanzó el límite de cambios mensuales para este plan'
            }
        
        # Validar límite de juegos
        limite = suscripcion.obtener_limite_juegos()
        if len(nuevos_juegos_ids) > limite:
            return {
                'exito': False,
                'error': f'El plan {suscripcion.tipo_suscripcion} permite máximo {limite} juegos'
            }
        
        # Obtener juegos válidos
        juegos = Juego.objects.filter(id__in=nuevos_juegos_ids, disponible=True)
        
        if juegos.count() != len(nuevos_juegos_ids):
            return {
                'exito': False,
                'error': 'Algunos juegos no están disponibles'
            }
        
        # Actualizar juegos
        suscripcion.juegos_seleccionados.set(juegos)
        suscripcion.cambios_mes_actual += 1
        suscripcion.save()
        
        return {
            'exito': True,
            'juegos_seleccionados': [j.nombre for j in juegos],
            'cambios_restantes': self._calcular_cambios_restantes(suscripcion)
        }
    
    # ========================================================================
    # CASO DE USO 4: Verificar acceso a un juego
    # ========================================================================
    
    def verificar_acceso_juego(self, suscripcion_id, juego_id):
        """
        Verifica si el usuario puede acceder a un juego específico.
        Esta es una de las reglas de negocio más importantes del sistema.
        
        Returns:
            Dict con el resultado de la verificación
        """
        try:
            suscripcion = Suscripcion.objects.get(id=suscripcion_id)
            juego = Juego.objects.get(id=juego_id)
        except (Suscripcion.DoesNotExist, Juego.DoesNotExist):
            return {
                'tiene_acceso': False,
                'motivo': 'Suscripción o juego no encontrado'
            }
        
        # Usar el método del dominio
        tiene_acceso = suscripcion.puede_acceder(juego)
        
        if not tiene_acceso:
            if suscripcion.estado != EstadoSuscripcion.ACTIVA:
                motivo = f'Suscripción en estado {suscripcion.estado}'
            elif suscripcion.tipo_suscripcion != TipoSuscripcion.VIP:
                motivo = 'Juego no incluido en tu selección. Cámbialo en tu perfil.'
            else:
                motivo = 'Juego no disponible'
        else:
            motivo = 'Acceso concedido'
        
        return {
            'tiene_acceso': tiene_acceso,
            'motivo': motivo,
            'tipo_suscripcion': suscripcion.tipo_suscripcion,
            'juego': juego.nombre
        }
    
    # ========================================================================
    # CASO DE USO 5: Procesar renovaciones pendientes
    # ========================================================================
    
    @transaction.atomic
    def procesar_renovaciones_pendientes(self):
        """
        Tarea programada que procesa las renovaciones pendientes.
        Envía notificaciones 7 días antes de la renovación.
        
        Returns:
            Dict con estadísticas del proceso
        """
        # Suscripciones que necesitan notificación
        suscripciones_notificar = Suscripcion.objects.filter(
            estado=EstadoSuscripcion.ACTIVA
        )
        
        notificaciones_enviadas = 0
        renovaciones_procesadas = 0
        expiraciones_procesadas = 0
        
        for suscripcion in suscripciones_notificar:
            # Enviar notificación si corresponde
            if suscripcion.requiere_notificacion():
                self.notificador.notificar_renovacion(suscripcion)
                suscripcion.notificacion_enviada = True
                suscripcion.marcar_para_renovacion()
                notificaciones_enviadas += 1
            
            # Procesar expiración si ya pasó la fecha
            if suscripcion.fecha_renovacion <= timezone.now():
                self._procesar_expiracion(suscripcion)
                expiraciones_procesadas += 1
        
        return {
            'notificaciones_enviadas': notificaciones_enviadas,
            'expiraciones_procesadas': expiraciones_procesadas
        }
    
    # ========================================================================
    # CASO DE USO 6: Renovar suscripción
    # ========================================================================
    
    @transaction.atomic
    def renovar_suscripcion(self, suscripcion_id, nuevo_tipo=None, metodo_pago='stripe'):
        """
        Renueva una suscripción, opcionalmente cambiando el tipo de plan.
        Procesa el pago correspondiente.
        
        Returns:
            Dict con el resultado de la renovación
        """
        try:
            suscripcion = Suscripcion.objects.get(id=suscripcion_id)
        except Suscripcion.DoesNotExist:
            return {
                'exito': False,
                'error': 'Suscripción no encontrada'
            }
        
        # Determinar el tipo a renovar
        tipo_renovacion = nuevo_tipo or suscripcion.tipo_suscripcion
        
        # Calcular precio
        monto = self.calculador_precio.calcular_precio_mensual(tipo_renovacion)
        
        # Procesar pago
        pago_resultado = self._procesar_pago_renovacion(
            suscripcion,
            monto,
            metodo_pago,
            tipo_renovacion
        )
        
        if not pago_resultado['exito']:
            return {
                'exito': False,
                'error': 'Error al procesar el pago de renovación'
            }
        
        # Renovar la suscripción usando el método del dominio
        tipo_anterior = suscripcion.tipo_suscripcion
        suscripcion.renovar(nuevo_tipo=tipo_renovacion)
        
        # Registrar en historial si cambió el tipo
        if nuevo_tipo and nuevo_tipo != tipo_anterior:
            HistorialCambioSuscripcion.objects.create(
                suscripcion=suscripcion,
                tipo_anterior=tipo_anterior,
                tipo_nuevo=tipo_renovacion,
                motivo=f'Renovación con cambio de plan (${monto})'
            )
        
        return {
            'exito': True,
            'tipo': tipo_renovacion,
            'monto': float(monto),
            'fecha_renovacion': suscripcion.fecha_renovacion,
            'transaccion_id': pago_resultado['transaccion_id']
        }
    
    # ========================================================================
    # Métodos privados auxiliares
    # ========================================================================
    
    def _procesar_pago_upgrade(self, suscripcion, monto, descripcion):
        """Procesa el pago de un upgrade"""
        procesador = ProcesadorPagoFactory.crear_procesador('stripe')
        referencia = f"UPG-{uuid.uuid4().hex[:12].upper()}"
        
        resultado_pago = procesador.procesar_pago(
            monto=float(monto),
            metodo_pago='stripe',
            referencia=referencia
        )
        
        if resultado_pago['exito']:
            # Crear registro de pago
            pago = Pago.objects.create(
                suscripcion=suscripcion,
                monto=monto,
                metodo_pago='stripe',
                estado='APROBADO',
                referencia=referencia
            )
        
        return resultado_pago
    
    def _procesar_pago_renovacion(self, suscripcion, monto, metodo_pago, tipo):
        """Procesa el pago de una renovación"""
        procesador = ProcesadorPagoFactory.crear_procesador(metodo_pago)
        referencia = f"REN-{uuid.uuid4().hex[:12].upper()}"
        
        resultado_pago = procesador.procesar_pago(
            monto=float(monto),
            metodo_pago=metodo_pago,
            referencia=referencia
        )
        
        if resultado_pago['exito']:
            Pago.objects.create(
                suscripcion=suscripcion,
                monto=monto,
                metodo_pago=metodo_pago,
                estado='APROBADO',
                referencia=referencia
            )
        
        return resultado_pago
    
    def _procesar_expiracion(self, suscripcion):
        """Marca una suscripción como expirada y notifica"""
        suscripcion.estado = EstadoSuscripcion.EXPIRADA
        suscripcion.save()
        self.notificador.notificar_expiracion(suscripcion)
    
    def _calcular_cambios_restantes(self, suscripcion):
        """Calcula cuántos cambios de juegos quedan en el mes"""
        if suscripcion.tipo_suscripcion == TipoSuscripcion.VIP:
            return 'ilimitados'
        elif suscripcion.tipo_suscripcion == TipoSuscripcion.PREMIUM:
            return 'ilimitados'
        else:  # NORMAL
            return max(0, 1 - suscripcion.cambios_mes_actual)