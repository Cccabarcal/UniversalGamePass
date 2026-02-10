from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal


# ============================================================================
# NOTIFICADORES - Factory para diferentes medios de notificación
# ============================================================================

class NotificadorBase(ABC):
    """Interfaz base para notificadores"""
    
    @abstractmethod
    def notificar_renovacion(self, suscripcion):
        """Notifica al usuario sobre la próxima renovación"""
        pass
    
    @abstractmethod
    def notificar_cambio_plan(self, suscripcion, tipo_anterior, tipo_nuevo):
        """Notifica al usuario sobre el cambio de plan"""
        pass
    
    @abstractmethod
    def notificar_expiracion(self, suscripcion):
        """Notifica al usuario sobre la expiración de su suscripción"""
        pass


class NotificadorEmail(NotificadorBase):
    """Implementación de notificador por correo electrónico"""
    
    def notificar_renovacion(self, suscripcion):
        """Envía email sobre renovación próxima"""
        dias = suscripcion.dias_hasta_renovacion()
        
        asunto = f"Tu suscripción {suscripcion.tipo_suscripcion} se renueva pronto"
        mensaje = f"""
        Hola {suscripcion.usuario.username},
        
        Tu suscripción {suscripcion.tipo_suscripcion} se renovará en {dias} días.
        Fecha de renovación: {suscripcion.fecha_renovacion.strftime('%d/%m/%Y')}
        
        ¿Deseas mantener tu plan actual o mejorarlo?
        - Plan actual: {suscripcion.tipo_suscripcion}
        - Juegos seleccionados: {suscripcion.juegos_seleccionados.count()}
        
        Ingresa a tu cuenta para gestionar tu suscripción.
        
        Saludos,
        Equipo UniversalGamePass Cloud
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [suscripcion.usuario.email],
            fail_silently=False,
        )
        
        return True
    
    def notificar_cambio_plan(self, suscripcion, tipo_anterior, tipo_nuevo):
        """Envía email confirmando cambio de plan"""
        asunto = "Cambio de plan confirmado"
        mensaje = f"""
        Hola {suscripcion.usuario.username},
        
        Tu plan ha sido actualizado exitosamente:
        - Plan anterior: {tipo_anterior}
        - Plan nuevo: {tipo_nuevo}
        
        Los cambios son efectivos de inmediato.
        
        Saludos,
        Equipo UniversalGamePass Cloud
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [suscripcion.usuario.email],
            fail_silently=False,
        )
        
        return True
    
    def notificar_expiracion(self, suscripcion):
        """Envía email sobre expiración de suscripción"""
        asunto = "Tu suscripción ha expirado"
        mensaje = f"""
        Hola {suscripcion.usuario.username},
        
        Tu suscripción {suscripcion.tipo_suscripcion} ha expirado.
        
        Para seguir disfrutando del servicio, renueva tu suscripción.
        
        Saludos,
        Equipo UniversalGamePass Cloud
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [suscripcion.usuario.email],
            fail_silently=False,
        )
        
        return True


class NotificadorSMS(NotificadorBase):
    """Implementación de notificador por SMS (simulado)"""
    
    def notificar_renovacion(self, suscripcion):
        """Envía SMS sobre renovación próxima"""
        # Simulación - en producción usaría Twilio, AWS SNS, etc.
        dias = suscripcion.dias_hasta_renovacion()
        print(f"[SMS] Renovación en {dias} días para {suscripcion.usuario.username}")
        return True
    
    def notificar_cambio_plan(self, suscripcion, tipo_anterior, tipo_nuevo):
        """Envía SMS confirmando cambio de plan"""
        print(f"[SMS] Plan cambiado de {tipo_anterior} a {tipo_nuevo}")
        return True
    
    def notificar_expiracion(self, suscripcion):
        """Envía SMS sobre expiración"""
        print(f"[SMS] Suscripción expirada para {suscripcion.usuario.username}")
        return True


class NotificadorFactory:
    """
    Factory para crear notificadores.
    Decide qué tipo de notificador instanciar según la configuración.
    """
    
    @staticmethod
    def crear_notificador(tipo='email'):
        """
        Crea y retorna un notificador según el tipo especificado.
        
        Args:
            tipo: 'email', 'sms', o 'multi' (ambos)
        
        Returns:
            Una instancia de NotificadorBase
        """
        if tipo == 'email':
            return NotificadorEmail()
        elif tipo == 'sms':
            return NotificadorSMS()
        elif tipo == 'multi':
            return NotificadorMultiple([NotificadorEmail(), NotificadorSMS()])
        else:
            # Por defecto, email
            return NotificadorEmail()


class NotificadorMultiple(NotificadorBase):
    """Notificador que envía por múltiples canales"""
    
    def __init__(self, notificadores):
        self.notificadores = notificadores
    
    def notificar_renovacion(self, suscripcion):
        resultados = [n.notificar_renovacion(suscripcion) for n in self.notificadores]
        return all(resultados)
    
    def notificar_cambio_plan(self, suscripcion, tipo_anterior, tipo_nuevo):
        resultados = [n.notificar_cambio_plan(suscripcion, tipo_anterior, tipo_nuevo) 
                     for n in self.notificadores]
        return all(resultados)
    
    def notificar_expiracion(self, suscripcion):
        resultados = [n.notificar_expiracion(suscripcion) for n in self.notificadores]
        return all(resultados)


# ============================================================================
# CALCULADORES DE PRECIOS - Factory para lógica de precios
# ============================================================================

class CalculadorPrecioBase(ABC):
    """Interfaz base para calculadores de precio"""
    
    @abstractmethod
    def calcular_precio_mensual(self, tipo_suscripcion):
        """Calcula el precio mensual según el tipo de suscripción"""
        pass
    
    @abstractmethod
    def calcular_precio_upgrade(self, tipo_actual, tipo_nuevo, dias_restantes):
        """Calcula el costo de un upgrade prorrateado"""
        pass


class CalculadorPrecioEstandar(CalculadorPrecioBase):
    """Calculador de precios estándar"""
    
    PRECIOS = {
        'NORMAL': Decimal('9.99'),
        'PREMIUM': Decimal('14.99'),
        'VIP': Decimal('24.99'),
    }
    
    def calcular_precio_mensual(self, tipo_suscripcion):
        """Retorna el precio mensual del plan"""
        return self.PRECIOS.get(tipo_suscripcion, Decimal('0.00'))
    
    def calcular_precio_upgrade(self, tipo_actual, tipo_nuevo, dias_restantes):
        """
        Calcula el costo de upgrade prorrateado.
        Cobra la diferencia proporcional a los días restantes.
        """
        precio_actual = self.PRECIOS.get(tipo_actual, Decimal('0.00'))
        precio_nuevo = self.PRECIOS.get(tipo_nuevo, Decimal('0.00'))
        
        diferencia = precio_nuevo - precio_actual
        
        if diferencia <= 0:
            return Decimal('0.00')  # No hay costo si es downgrade
        
        # Prorrateo: (diferencia * días_restantes) / 30
        costo_prorrateado = (diferencia * Decimal(dias_restantes)) / Decimal('30')
        
        return costo_prorrateado.quantize(Decimal('0.01'))


class CalculadorPrecioPromocional(CalculadorPrecioBase):
    """Calculador con descuentos promocionales"""
    
    PRECIOS = {
        'NORMAL': Decimal('7.99'),   # 20% descuento
        'PREMIUM': Decimal('11.99'),  # 20% descuento
        'VIP': Decimal('19.99'),      # 20% descuento
    }
    
    def calcular_precio_mensual(self, tipo_suscripcion):
        return self.PRECIOS.get(tipo_suscripcion, Decimal('0.00'))
    
    def calcular_precio_upgrade(self, tipo_actual, tipo_nuevo, dias_restantes):
        precio_actual = self.PRECIOS.get(tipo_actual, Decimal('0.00'))
        precio_nuevo = self.PRECIOS.get(tipo_nuevo, Decimal('0.00'))
        
        diferencia = precio_nuevo - precio_actual
        
        if diferencia <= 0:
            return Decimal('0.00')
        
        costo_prorrateado = (diferencia * Decimal(dias_restantes)) / Decimal('30')
        return costo_prorrateado.quantize(Decimal('0.01'))


class CalculadorPrecioFactory:
    """
    Factory para crear calculadores de precio.
    Permite cambiar la estrategia de precios fácilmente.
    """
    
    @staticmethod
    def crear_calculador(tipo='estandar'):
        """
        Crea y retorna un calculador de precios.
        
        Args:
            tipo: 'estandar' o 'promocional'
        
        Returns:
            Una instancia de CalculadorPrecioBase
        """
        if tipo == 'promocional':
            return CalculadorPrecioPromocional()
        else:
            return CalculadorPrecioEstandar()


# ============================================================================
# PROCESADORES DE PAGO - Factory para diferentes pasarelas de pago
# ============================================================================

class ProcesadorPagoBase(ABC):
    """Interfaz base para procesadores de pago"""
    
    @abstractmethod
    def procesar_pago(self, monto, metodo_pago, referencia):
        """Procesa un pago y retorna el resultado"""
        pass


class ProcesadorPayPal(ProcesadorPagoBase):
    """Procesador de pagos con PayPal (simulado)"""
    
    def procesar_pago(self, monto, metodo_pago, referencia):
        """Simula el procesamiento con PayPal"""
        print(f"[PayPal] Procesando ${monto} - Ref: {referencia}")
        # En producción, aquí iría la integración con PayPal API
        return {
            'exito': True,
            'transaccion_id': f"PP-{referencia}",
            'monto': monto,
            'metodo': 'PayPal'
        }


class ProcesadorStripe(ProcesadorPagoBase):
    """Procesador de pagos con Stripe (simulado)"""
    
    def procesar_pago(self, monto, metodo_pago, referencia):
        """Simula el procesamiento con Stripe"""
        print(f"[Stripe] Procesando ${monto} - Ref: {referencia}")
        # En producción, aquí iría la integración con Stripe API
        return {
            'exito': True,
            'transaccion_id': f"ST-{referencia}",
            'monto': monto,
            'metodo': 'Stripe'
        }


class ProcesadorPagoFactory:
    """Factory para crear procesadores de pago"""
    
    @staticmethod
    def crear_procesador(metodo='stripe'):
        """
        Crea y retorna un procesador de pago.
        
        Args:
            metodo: 'stripe', 'paypal', etc.
        
        Returns:
            Una instancia de ProcesadorPagoBase
        """
        if metodo == 'paypal':
            return ProcesadorPayPal()
        else:
            return ProcesadorStripe()
