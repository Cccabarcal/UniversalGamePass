# UniversalGamePass - Ejemplos de Uso del API

> Ejemplos de cURL y HTTPie para probar todos los endpoints del Strangler Pattern

## 📌 Base URLs

```
Local Gateway:  http://localhost
Django direct:  http://localhost:8000
Flask direct:   http://localhost:5000
```

---

## 🏠 Health Checks

```bash
# Nginx Gateway Health
curl http://localhost/health | jq

# Flask Health (directo)
curl http://localhost:5000/health | jq
```

**Respuesta esperada**:
```json
{
  "status": "healthy",
  "service": "reports",
  "api_version": "v2",
  "timestamp": "2026-04-13T10:30:00"
}
```

---

## 📊 Flask API - Reportes (v2)

### 1. Resumen de Transacciones

```bash
# Últimos 30 días
curl "http://localhost/api/v2/reportes/resumen-transacciones?dias=30" | jq

# Últimos 90 días
curl "http://localhost/api/v2/reportes/resumen-transacciones?dias=90" | jq

# Por usuario específico
curl "http://localhost/api/v2/reportes/resumen-transacciones?dias=30&user_id=1" | jq
```

**Respuesta esperada**:
```json
{
  "resumen": {
    "total_ingresos": 1500.50,
    "transacciones_completadas": 15,
    "transacciones_pendientes": 2,
    "transacciones_fallidas": 1,
    "promedio_transaccion": 100.03
  },
  "por_tipo": {
    "suscripcion": {
      "cantidad": 10,
      "monto": 1000.00
    },
    "compra_juego": {
      "cantidad": 5,
      "monto": 400.00
    },
    "reembolso": {
      "cantidad": 2,
      "monto": -100.00
    }
  },
  "periodo": {
    "inicio": "2026-03-14",
    "fin": "2026-04-13",
    "dias": 30
  }
}
```

---

### 2. Crecimiento de Suscripciones

```bash
# Últimos 3 meses
curl "http://localhost/api/v2/reportes/crecimiento-suscripciones?meses=3" | jq

# Últimos 12 meses
curl "http://localhost/api/v2/reportes/crecimiento-suscripciones?meses=12" | jq
```

**Respuesta esperada**:
```json
{
  "crecimiento": [
    {
      "mes": "2026-02",
      "nuevas_suscripciones": 5,
      "canceladas": 1
    },
    {
      "mes": "2026-03",
      "nuevas_suscripciones": 8,
      "canceladas": 0
    },
    {
      "mes": "2026-04",
      "nuevas_suscripciones": 3,
      "canceladas": 1
    }
  ],
  "total_activas": 15,
  "churn_rate": 0.067,
  "meses_analizados": 3
}
```

---

### 3. Juegos Más Usados

```bash
# Top 10 (default)
curl "http://localhost/api/v2/reportes/juegos-mas-usados" | jq

# Top 5
curl "http://localhost/api/v2/reportes/juegos-mas-usados?limit=5" | jq

# Top 20, últimos 60 días
curl "http://localhost/api/v2/reportes/juegos-mas-usados?limit=20&dias=60" | jq
```

**Respuesta esperada**:
```json
{
  "juegos": [
    {
      "id": 1,
      "nombre": "The Last of Us",
      "compras": 12,
      "ingresos": 599.88
    },
    {
      "id": 2,
      "nombre": "God of War",
      "compras": 8,
      "ingresos": 399.92
    },
    {
      "id": 3,
      "nombre": "Elden Ring",
      "compras": 6,
      "ingresos": 299.94
    }
  ],
  "periodo_dias": 30,
  "limit": 10
}
```

---

### 4. Estadísticas por Usuario

```bash
# Usuario ID 1
curl "http://localhost/api/v2/reportes/estadisticas-usuario/1" | jq

# Usuario ID 42
curl "http://localhost/api/v2/reportes/estadisticas-usuario/42" | jq
```

**Respuesta esperada**:
```json
{
  "user_id": 1,
  "total_gastado": 450.50,
  "transacciones": 5,
  "suscripciones_activas": 1,
  "juegos_comprados": 2,
  "ultima_transaccion": "2026-04-10T14:30:00",
  "generado_en": "2026-04-13T10:30:00"
}
```

---

### 5. Estado de Pagos

```bash
# Todos los estados
curl "http://localhost/api/v2/reportes/estado-pagos" | jq

# Solo completadas
curl "http://localhost/api/v2/reportes/estado-pagos?estado=completada" | jq

# Solo pendientes
curl "http://localhost/api/v2/reportes/estado-pagos?estado=pendiente" | jq
```

**Respuesta esperada**:
```json
{
  "distribucion": {
    "completada": {
      "cantidad": 50,
      "porcentaje": 83.33
    },
    "pendiente": {
      "cantidad": 8,
      "porcentaje": 13.34
    },
    "fallida": {
      "cantidad": 2,
      "porcentaje": 3.33
    },
    "cancelada": {
      "cantidad": 0,
      "porcentaje": 0.0
    }
  },
  "total_transacciones": 60,
  "estado_filtrado": "completada"
}
```

---

## 🐍 Django API - Legacy (v1)

### Planes

```bash
# Listar todos
curl "http://localhost/api/planes/" | jq

# Détalle específico
curl "http://localhost/api/planes/1/" | jq
```

---

### Videojuegos

```bash
# Listar todos
curl "http://localhost/api/videojuegos/" | jq

# Détalle específico
curl "http://localhost/api/videojuegos/1/" | jq
```

---

### Suscripciones (Requiere autenticación)

```bash
# Listar mis suscripciones
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/suscripciones/" | jq

# Crear suscripción
curl -X POST "http://localhost/api/suscripciones/crear/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": 1, "renovacion_automatica": true}' | jq
```

---

### Transacciones (Requiere autenticación)

```bash
# Listar mis transacciones
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/transacciones/" | jq

# Détalle de transacción
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/transacciones/1/" | jq
```

---

## 🧪 Tests Automatizados

### Verificar Strangler Routing

```bash
#!/bin/bash

echo "🧪 Testing Strangler Pattern Routing"
echo ""

echo "1. Verificar que /api/v1 va a Django:"
curl -s "http://localhost/api/planes/" | grep -q "nombre" && echo "✅ OK" || echo "❌ FAIL"

echo "2. Verificar que /api/v2/reportes va a Flask:"
curl -s "http://localhost/api/v2/reportes/resumen-transacciones" | grep -q "resumen" && echo "✅ OK" || echo "❌ FAIL"

echo "3. Verificar Nginx Health:"
curl -s "http://localhost/health" | grep -q "healthy" && echo "✅ OK" || echo "❌ FAIL"

echo "4. Verificar Flask Health:"
curl -s "http://localhost:5000/health" | grep -q "healthy" && echo "✅ OK" || echo "❌ FAIL"

echo ""
echo "✅ All routing tests completed!"
```

---

## 📊 Performance Testing

### Load Test en Reportes

```bash
# Simular 100 requests concurrentes
ab -n 100 -c 10 "http://localhost/api/v2/reportes/resumen-transacciones"

# Stress test: 1000 requests, 50 concurrentes
ab -n 1000 -c 50 "http://localhost/api/v2/reportes/resumen-transacciones"

# Con datos variables
ab -n 100 -c 10 "http://localhost/api/v2/reportes/resumen-transacciones?dias=30"
```

### Load Test en Django

```bash
# Comparar rendimiento: Django sin reportes pesados
ab -n 100 -c 10 "http://localhost/api/planes/"
```

---

## 🔍 Debugging

### Ver headers de respuesta

```bash
# Incluir headers
curl -i "http://localhost/api/v2/reportes/resumen-transacciones"

# Verbose (ver request y response completos)
curl -v "http://localhost/api/v2/reportes/resumen-transacciones"
```

### Ver ruta de routeo en Nginx

```bash
# Header X-Forwarded-For muestra el reverso proxy
curl -i "http://localhost/api/v2/reportes/resumen-transacciones" | grep -i "x-"
```

### Verificar resolución DNS (Docker)

```bash
# Desde dentro del contenedor
docker-compose exec nginx ping django_web
docker-compose exec nginx ping flask_reports
```

---

## 📝 Usando HTTPie (alternativa a curl)

HTTPie es más legible que curl:

```bash
# Instalar: pip install httpie

# GET request
http GET http://localhost/api/v2/reportes/resumen-transacciones dias==30

# Pretty print (automático)
http GET http://localhost/api/v2/reportes/resumen-transacciones

# Con headers
http GET http://localhost/health Content-Type:application/json

# POST request
http POST http://localhost/api/suscripciones/crear \
  Authorization:"Bearer TOKEN" \
  plan_id:=1 \
  renovacion_automatica:=true
```

---

## ✖️ Manejo de Errores

### Parámetros inválidos

```bash
# Días negativo
curl "http://localhost/api/v2/reportes/resumen-transacciones?dias=-5"
→ 400 {"error": "dias debe estar entre 1 y 365", "code": "VALIDATION_ERROR"}

# User ID inválido
curl "http://localhost/api/v2/reportes/estadisticas-usuario/-1"
→ 400 {"error": "user_id debe ser un entero positivo", "code": "VALIDATION_ERROR"}

# Estado inválido
curl "http://localhost/api/v2/reportes/estado-pagos?estado=invalido"
→ 400 {"error": "estado debe ser uno de: ...", "code": "VALIDATION_ERROR"}
```

### Endpoint no existe

```bash
curl "http://localhost/api/v2/reportes/endpoint-inexistente"
→ 404 {"error": "Endpoint no encontrado", "code": "NOT_FOUND"}
```

### Método HTTP no permitido

```bash
curl -X PUT "http://localhost/api/v2/reportes/resumen-transacciones"
→ 405 {"error": "Método HTTP no permitido", "code": "METHOD_NOT_ALLOWED"}
```

---

## 🎯 Casos de Uso Completos

### Caso 1: Reportes de Ingresos del Mes

```bash
# 1. Obtener resumen
RESUMEN=$(curl -s "http://localhost/api/v2/reportes/resumen-transacciones?dias=30")
echo "Ingresos del mes: $(echo $RESUMEN | jq '.resumen.total_ingresos')"

# 2. Obtener distribución por tipo
echo $RESUMEN | jq '.por_tipo'

# 3. Verificar transacciones fallidas
FALLIDAS=$(echo $RESUMEN | jq '.resumen.transacciones_fallidas')
echo "Transacciones fallidas: $FALLIDAS"
```

### Caso 2: Análisis de Crecimiento

```bash
# 1. Obtener crecimiento últimos 6 meses
CREC=$(curl -s "http://localhost/api/v2/reportes/crecimiento-suscripciones?meses=6")
echo $CREC | jq '.crecimiento[] | {mes, nuevas: .nuevas_suscripciones}'

# 2. Calcular churn rate
echo "Churn rate: $(echo $CREC | jq '.churn_rate')"

# 3. Total de activas
echo "Suscripciones activas: $(echo $CREC | jq '.total_activas')"
```

### Caso 3: Top Games Dashboard

```bash
# 1. Top 5 juegos
TOP5=$(curl -s "http://localhost/api/v2/reportes/juegos-mas-usados?limit=5")
echo $TOP5 | jq '.juegos[] | {nombre, compras, ingresos}'

# 2. Ingresos totales por juegos
TOTAL=$(echo $TOP5 | jq '[.juegos[].ingresos] | add')
echo "Ingresos totales (top 5): $TOTAL"
```

---

## 📚 Documentación Adicional

- `README_DOCKER.md` - Guía de instalación
- `DECISION_MATRIX.md` - Justificación arquitectónica
- `WIKI_STRANGLER_PATTERN.md` - Documentación técnica completa
- `reports_service/app.py` - Código comentado de endpoints

---

**Última actualización**: 2026-04-13
