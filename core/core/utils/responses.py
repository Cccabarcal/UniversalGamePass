"""
Utilidades para respuestas JSON estándar
Centraliza el formato de respuestas en toda la API
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Generador de respuestas JSON estándar con estado"""

    @staticmethod
    def success(data=None, message="Operación exitosa", status_code=status.HTTP_200_OK):
        """Respuesta exitosa"""
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data
            },
            status=status_code
        )

    @staticmethod
    def created(data=None, message="Recurso creado exitosamente", status_code=status.HTTP_201_CREATED):
        """Recurso creado"""
        return Response(
            {
                "status": "created",
                "message": message,
                "data": data
            },
            status=status_code
        )

    @staticmethod
    def error(message="Error en la solicitud", error_code="ERROR", status_code=status.HTTP_400_BAD_REQUEST):
        """Error en la solicitud"""
        return Response(
            {
                "status": "error",
                "message": message,
                "error_code": error_code
            },
            status=status_code
        )

    @staticmethod
    def validation_error(errors, message="Validación fallida", status_code=status.HTTP_400_BAD_REQUEST):
        """Error de validación"""
        return Response(
            {
                "status": "validation_error",
                "message": message,
                "errors": errors
            },
            status=status_code
        )

    @staticmethod
    def not_found(message="Recurso no encontrado"):
        """Recurso no encontrado"""
        return Response(
            {
                "status": "not_found",
                "message": message,
                "error_code": "RESOURCE_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def forbidden(message="No tienes permiso para acceder a este recurso"):
        """Acceso denegado"""
        return Response(
            {
                "status": "forbidden",
                "message": message,
                "error_code": "ACCESS_DENIED"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def conflict(message="Conflicto en la solicitud", conflict_code="CONFLICT"):
        """Conflicto (ej: duplicado)"""
        return Response(
            {
                "status": "conflict",
                "message": message,
                "conflict_code": conflict_code
            },
            status=status.HTTP_409_CONFLICT
        )

    @staticmethod
    def server_error(message="Error del servidor"):
        """Error del servidor"""
        return Response(
            {
                "status": "server_error",
                "message": message,
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
