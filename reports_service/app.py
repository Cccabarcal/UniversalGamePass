"""
Flask Microservicio: UniversalGamePass Reports Service
Generación de reportes de transacciones y estadísticas de uso.
API REST JSON que se comunica con Django como fuente de datos.
"""

from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)

# Configuración básica
API_VERSION = "v2"
SERVICE_NAME = "reports"

# Request/Response headers
def json_response(func):
    """Decorator para asegurar respuestas JSON con headers correctos."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, tuple):
                return result
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
        except KeyError as e:
            return jsonify({"error": f"Missing field: {str(e)}", "code": "MISSING_FIELD"}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR"}), 500
    return wrapper


# Health Check
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check para Docker y Nginx."""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "api_version": API_VERSION,
        "timestamp": datetime.now().isoformat()
    }), 200


# ============================================================================
# API Endpoints: /api/v2/reportes/*
# ============================================================================

@app.route(f'/api/{API_VERSION}/reportes/resumen-transacciones', methods=['GET'])
@json_response
def resumen_transacciones():
    """
    GET /api/v2/reportes/resumen-transacciones
    
    Retorna un resumen de transacciones por estado.
    Query params:
    - user_id: (opcional) filtrar por usuario
    - dias: (default 30) últimos N días
    
    Response:
    {
        "resumen": {
            "total_ingresos": 1500.50,
            "transacciones_completadas": 15,
            "transacciones_pendientes": 2,
            "transacciones_fallidas": 1,
            "promedio_transaccion": 100.03
        },
        "por_tipo": {
            "suscripcion": {"cantidad": 10, "monto": 1000.00},
            "compra_juego": {"cantidad": 5, "monto": 400.00},
            "reembolso": {"cantidad": 2, "monto": -100.00}
        },
        "periodo": {"inicio": "2026-03-14", "fin": "2026-04-13"}
    }
    """
    user_id = request.args.get('user_id')
    dias = int(request.args.get('dias', 30))
    
    if dias < 1 or dias > 365:
        raise ValueError("dias debe estar entre 1 y 365")
    
    # Simulación de datos. En producción, consultar BD real
    fecha_inicio = (datetime.now() - timedelta(days=dias)).date()
    fecha_fin = datetime.now().date()
    
    return {
        "resumen": {
            "total_ingresos": 1500.50,
            "transacciones_completadas": 15,
            "transacciones_pendientes": 2,
            "transacciones_fallidas": 1,
            "promedio_transaccion": 100.03
        },
        "por_tipo": {
            "suscripcion": {"cantidad": 10, "monto": 1000.00},
            "compra_juego": {"cantidad": 5, "monto": 400.00},
            "reembolso": {"cantidad": 2, "monto": -100.00}
        },
        "periodo": {
            "inicio": fecha_inicio.isoformat(),
            "fin": fecha_fin.isoformat(),
            "dias": dias
        }
    }


@app.route(f'/api/{API_VERSION}/reportes/crecimiento-suscripciones', methods=['GET'])
@json_response
def crecimiento_suscripciones():
    """
    GET /api/v2/reportes/crecimiento-suscripciones
    
    Retorna crecimiento de suscripciones por plan en el período solicitado.
    Query params:
    - meses: (default 3) últimos N meses
    
    Response:
    {
        "crecimiento": [
            {"mes": "2026-02", "nuevas_suscripciones": 5, "canceladas": 1},
            {"mes": "2026-03", "nuevas_suscripciones": 8, "canceladas": 0},
            {"mes": "2026-04", "nuevas_suscripciones": 3, "canceladas": 1}
        ],
        "total_activas": 15,
        "churn_rate": 0.067
    }
    """
    meses = int(request.args.get('meses', 3))
    
    if meses < 1 or meses > 24:
        raise ValueError("meses debe estar entre 1 y 24")
    
    return {
        "crecimiento": [
            {"mes": "2026-02", "nuevas_suscripciones": 5, "canceladas": 1},
            {"mes": "2026-03", "nuevas_suscripciones": 8, "canceladas": 0},
            {"mes": "2026-04", "nuevas_suscripciones": 3, "canceladas": 1}
        ],
        "total_activas": 15,
        "churn_rate": 0.067,
        "meses_analizados": meses
    }


@app.route(f'/api/{API_VERSION}/reportes/juegos-mas-usados', methods=['GET'])
@json_response
def juegos_mas_usados():
    """
    GET /api/v2/reportes/juegos-mas-usados
    
    Retorna los videojuegos más comprados/usados en el período.
    Query params:
    - limit: (default 10) top N juegos
    - dias: (default 30) últimos N días
    
    Response:
    {
        "juegos": [
            {"id": 1, "nombre": "The Last of Us", "compras": 12, "ingresos": 599.88},
            {"id": 2, "nombre": "God of War", "compras": 8, "ingresos": 399.92}
        ],
        "periodo_dias": 30
    }
    """
    limit = int(request.args.get('limit', 10))
    dias = int(request.args.get('dias', 30))
    
    if limit < 1 or limit > 100:
        raise ValueError("limit debe estar entre 1 y 100")
    if dias < 1 or dias > 365:
        raise ValueError("dias debe estar entre 1 y 365")
    
    return {
        "juegos": [
            {"id": 1, "nombre": "The Last of Us", "compras": 12, "ingresos": 599.88},
            {"id": 2, "nombre": "God of War", "compras": 8, "ingresos": 399.92},
            {"id": 3, "nombre": "Elden Ring", "compras": 6, "ingresos": 299.94}
        ],
        "periodo_dias": dias,
        "limit": limit
    }


@app.route(f'/api/{API_VERSION}/reportes/estadisticas-usuario/<int:user_id>', methods=['GET'])
@json_response
def estadisticas_usuario(user_id):
    """
    GET /api/v2/reportes/estadisticas-usuario/{user_id}
    
    Retorna estadísticas personalizadas de un usuario específico.
    
    Response:
    {
        "user_id": 1,
        "total_gastado": 450.50,
        "transacciones": 5,
        "suscripciones_activas": 1,
        "juegos_comprados": 2,
        "ultima_transaccion": "2026-04-10T14:30:00"
    }
    """
    if user_id < 1:
        raise ValueError("user_id debe ser un entero positivo")
    
    return {
        "user_id": user_id,
        "total_gastado": 450.50,
        "transacciones": 5,
        "suscripciones_activas": 1,
        "juegos_comprados": 2,
        "ultima_transaccion": "2026-04-10T14:30:00",
        "generado_en": datetime.now().isoformat()
    }


@app.route(f'/api/{API_VERSION}/reportes/estado-pagos', methods=['GET'])
@json_response
def estado_pagos():
    """
    GET /api/v2/reportes/estado-pagos
    
    Retorna análisis de estado de pagos (completados, pendientes, fallidos).
    Query params:
    - estado: (opcional) filtrar por estado específico
    
    Response:
    {
        "distribucion": {
            "completada": {"cantidad": 50, "porcentaje": 83.33},
            "pendiente": {"cantidad": 8, "porcentaje": 13.34},
            "fallida": {"cantidad": 2, "porcentaje": 3.33},
            "cancelada": {"cantidad": 0, "porcentaje": 0.00}
        },
        "total_transacciones": 60
    }
    """
    estado_filtro = request.args.get('estado')
    
    distribucion = {
        "completada": {"cantidad": 50, "porcentaje": 83.33},
        "pendiente": {"cantidad": 8, "porcentaje": 13.34},
        "fallida": {"cantidad": 2, "porcentaje": 3.33},
        "cancelada": {"cantidad": 0, "porcentaje": 0.00}
    }
    
    if estado_filtro and estado_filtro not in distribucion:
        raise ValueError(f"estado debe ser uno de: {', '.join(distribucion.keys())}")
    
    return {
        "distribucion": distribucion,
        "total_transacciones": 60,
        "estado_filtrado": estado_filtro
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Manejo global de rutas no encontradas."""
    return jsonify({
        "error": "Endpoint no encontrado",
        "code": "NOT_FOUND",
        "path": request.path
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Manejo global de métodos HTTP no permitidos."""
    return jsonify({
        "error": "Método HTTP no permitido",
        "code": "METHOD_NOT_ALLOWED",
        "method": request.method,
        "path": request.path
    }), 405


if __name__ == '__main__':
    # En desarrollo
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
