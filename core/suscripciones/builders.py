from datetime import timedelta
from django.utils import timezone
from .models import Suscripcion, TipoSuscripcion, EstadoSuscripcion


class SuscripcionBuilder:
    """
    Builder para construir objetos Suscripcion validados.
    Implementa el patrón Builder para separar la construcción
    de un objeto complejo de su representación.
    """
    
    def __init__(self):
        self._suscripcion = None
        self._errores = []
    
    def crear_nueva(self, usuario):
        """Inicializa una nueva suscripción para un usuario"""
        self._suscripcion = Suscripcion(usuario=usuario)
        self._errores = []
        return self
    
    def con_tipo(self, tipo_suscripcion):
        """
        Establece el tipo de suscripción.
        Valida que sea un tipo válido.
        """
        if tipo_suscripcion not in [choice[0] for choice in TipoSuscripcion.choices]:
            self._errores.append(f"Tipo de suscripción inválido: {tipo_suscripcion}")
            return self
        
        self._suscripcion.tipo_suscripcion = tipo_suscripcion
        return self
    
    def con_estado(self, estado):
        """Establece el estado de la suscripción"""
        if estado not in [choice[0] for choice in EstadoSuscripcion.choices]:
            self._errores.append(f"Estado inválido: {estado}")
            return self
        
        self._suscripcion.estado = estado
        return self
    
    def con_duracion_dias(self, dias=30):
        """
        Establece la fecha de renovación según la duración en días.
        Por defecto, las suscripciones duran 30 días.
        """
        if dias <= 0:
            self._errores.append("La duración debe ser mayor a 0 días")
            return self
        
        self._suscripcion.fecha_renovacion = timezone.now() + timedelta(days=dias)
        return self
    
    def con_juegos_seleccionados(self, lista_juegos):
        """
        Establece los juegos seleccionados.
        Valida que no exceda el límite según el tipo de suscripción.
        """
        if not self._suscripcion.tipo_suscripcion:
            self._errores.append("Debe establecer el tipo de suscripción antes de seleccionar juegos")
            return self
        
        limite = self._obtener_limite_juegos()
        
        if len(lista_juegos) > limite:
            self._errores.append(
                f"El plan {self._suscripcion.tipo_suscripcion} permite máximo {limite} juegos, "
                f"pero se intentaron seleccionar {len(lista_juegos)}"
            )
            return self
        
        # Guardamos los IDs para asignarlos después del save()
        self._juegos_pendientes = lista_juegos
        return self
    
    def activar(self):
        """Establece la suscripción como activa"""
        self._suscripcion.estado = EstadoSuscripcion.ACTIVA
        return self
    
    def _obtener_limite_juegos(self):
        """Retorna el límite de juegos según el tipo de suscripción"""
        limites = {
            TipoSuscripcion.NORMAL: 3,
            TipoSuscripcion.PREMIUM: 5,
            TipoSuscripcion.VIP: float('inf')
        }
        return limites.get(self._suscripcion.tipo_suscripcion, 0)
    
    def validar(self):
        """
        Valida que la suscripción esté lista para ser guardada.
        Retorna True si es válida, False si hay errores.
        """
        if not self._suscripcion:
            self._errores.append("No se ha inicializado la suscripción")
            return False
        
        if not self._suscripcion.usuario:
            self._errores.append("El usuario es obligatorio")
        
        if not self._suscripcion.tipo_suscripcion:
            self._errores.append("El tipo de suscripción es obligatorio")
        
        if not self._suscripcion.fecha_renovacion:
            self._errores.append("La fecha de renovación es obligatoria")
        
        if not self._suscripcion.estado:
            self._errores.append("El estado es obligatorio")
        
        return len(self._errores) == 0
    
    def obtener_errores(self):
        """Retorna la lista de errores de validación"""
        return self._errores.copy()
    
    def construir(self):
        """
        Construye y retorna la suscripción si es válida.
        Lanza una excepción si hay errores de validación.
        """
        if not self.validar():
            raise ValueError(f"Suscripción inválida: {', '.join(self._errores)}")
        
        # Guardamos la suscripción en la base de datos
        self._suscripcion.save()
        
        # Si hay juegos pendientes, los asignamos (relación Many-to-Many)
        if hasattr(self, '_juegos_pendientes'):
            self._suscripcion.juegos_seleccionados.set(self._juegos_pendientes)
        
        return self._suscripcion
    
    def reset(self):
        """Reinicia el builder para construir una nueva suscripción"""
        self._suscripcion = None
        self._errores = []
        if hasattr(self, '_juegos_pendientes'):
            delattr(self, '_juegos_pendientes')
        return self


# Clase Director (opcional) - coordina la construcción de tipos comunes
class DirectorSuscripcion:
    """
    Director que conoce las configuraciones comunes de suscripciones.
    Simplifica la creación de suscripciones estándar.
    """
    
    def __init__(self, builder):
        self._builder = builder
    
    def construir_suscripcion_normal(self, usuario, juegos):
        """Construye una suscripción Normal estándar"""
        return (self._builder
                .crear_nueva(usuario)
                .con_tipo(TipoSuscripcion.NORMAL)
                .con_duracion_dias(30)
                .con_juegos_seleccionados(juegos)
                .activar()
                .construir())
    
    def construir_suscripcion_premium(self, usuario, juegos):
        """Construye una suscripción Premium estándar"""
        return (self._builder
                .crear_nueva(usuario)
                .con_tipo(TipoSuscripcion.PREMIUM)
                .con_duracion_dias(30)
                .con_juegos_seleccionados(juegos)
                .activar()
                .construir())
    
    def construir_suscripcion_vip(self, usuario):
        """Construye una suscripción VIP estándar (acceso a todo)"""
        return (self._builder
                .crear_nueva(usuario)
                .con_tipo(TipoSuscripcion.VIP)
                .con_duracion_dias(30)
                .activar()
                .construir())
    
    def construir_suscripcion_trial(self, usuario, juegos):
        """Construye una suscripción de prueba (7 días)"""
        return (self._builder
                .crear_nueva(usuario)
                .con_tipo(TipoSuscripcion.NORMAL)
                .con_duracion_dias(7)
                .con_juegos_seleccionados(juegos)
                .activar()
                .construir())
