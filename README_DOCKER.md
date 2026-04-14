# UniversalGamePass - Taller 02: Patrón Estrangulador

## 🎮 Descripción

Plataforma de emulación de videojuegos en contexto educativo (tipo GeForce Now) implementada con **Strangler Pattern** para migraciones híbridas monolito → microservicios.

**Tecnologías**:
- **Monolito**: Django 5.2 + DRF
- **Microservicio**: Flask 3.0 (Reportes)
- **Orquestación**: Docker + Docker-Compose
- **API Gateway**: Nginx

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Docker >= 20.10
- Docker-Compose >= 2.0
- Python 3.12+ (para desarrollo local sin Docker)

### Levantar el Proyecto

```bash
# Clonar/Navegar al proyecto
cd UniversalGamePass

# Construir imágenes Docker
docker-compose build

# Levantar servicios (puerto 80)
docker-compose up

# En otra terminal, inicializar BD (primera vez)
docker-compose exec django_web python manage.py migrate
docker-compose exec django_web python manage.py createsuperuser
```

### Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Home** | http://localhost | Página principal (Django templates) |
| **Admin** | http://localhost/admin/ | Panel administrativo |
| **API v1** | http://localhost/api/v1/* | APIs legacy (Django) |
| **API v2 Reportes** | http://localhost/api/v2/reportes/* | Reportes (Flask microservicio) |
| **Health** | http://localhost/health | Gateway health check |

---

## 📁 Estructura del Proyecto

```
UniversalGamePass/
│
├── core/                          # Django Monolito
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile                 # Para Django en contenedor
│   ├── db.sqlite3                 # BD local (volumen Docker)
│   └── core/
│       ├── settings.py
│       ├── urls.py
│       ├── views.py               # APIs REST + HTML views
│       ├── models.py
│       ├── serializers.py
│       ├── services.py
│       ├── wsgi.py
│       ├── asgi.py
│       ├── admin.py
│       ├── domain/
│       │   └── builders.py        # Builder pattern (Suscripciones)
│       ├── infra/
│       │   └── factories.py       # Factory pattern (Notificadores)
│       └── migrations/
│
├── reports_service/               # Flask Microservicio (NEW)
│   ├── app.py                     # Aplicación Flask con 5 endpoints
│   ├── requirements.txt           # Flask + Gunicorn
│   └── Dockerfile                 # Multi-stage build
│
├── docker-compose.yml             # Orquestación (Nginx + Django + Flask)
├── nginx.conf                     # API Gateway (Strangler routing)
├── DECISION_MATRIX.md             # Matriz de decisión justificada
├── WIKI_STRANGLER_PATTERN.md      # Documentación completa para Wiki
├── .dockerignore
├── README.md                       # Este archivo
└── requirements.txt               # Dependencias Django

```

---

## 🏗️ Arquitectura: Strangler Pattern

### Diagrama de Flujo

```
Internet (80)
    ▼
┌────────────────────────────┐
│   Nginx API Gateway        │  ← Bifurca tráfico
└──────┬─────────┬───────────┘
       │         │
  /api/v1/*  /api/v2/reportes/*
       │         │
       ▼         ▼
   Django      Flask
   (8000)      (5000)
   Monolito    Reportes
       │         │
       └────┬────┘
            ▼
        BD SQLite
```

### Routeo Inteligente

| URL Pattern | Backend | Descripción |
|-------------|---------|------------|
| `/` | Django | Home page, vistas HTML |
| `/admin/` | Django | Admin panel |
| `/accounts/*` | Django | Auth (login/signup) |
| `/api/v1/*` | Django | API original |
| **`/api/v2/reportes/*`** | **Flask** | ✨ **Estrangulado** |

---

## 📊 API Endpoints

### Django API (v1)

```bash
# Planes
GET  /api/planes/
GET  /api/planes/{id}/

# Videojuegos
GET  /api/videojuegos/
GET  /api/videojuegos/{id}/

# Suscripciones (requiere autenticación)
GET  /api/suscripciones/
POST /api/suscripciones/crear/
GET  /api/suscripciones/{id}/

# Transacciones (requiere autenticación)
GET  /api/transacciones/
GET  /api/transacciones/{id}/
```

### Flask API (v2 - Reportes) ⭐ NEW

```bash
# Health check
GET  /health

# Resumen de transacciones
GET  /api/v2/reportes/resumen-transacciones?dias=30&user_id=1

# Crecimiento de suscripciones
GET  /api/v2/reportes/crecimiento-suscripciones?meses=3

# Juegos más usados
GET  /api/v2/reportes/juegos-mas-usados?limit=10&dias=30

# Estadísticas por usuario
GET  /api/v2/reportes/estadisticas-usuario/{user_id}

# Estado de pagos
GET  /api/v2/reportes/estado-pagos?estado=completada
```

---

## 🧪 Testing

### Unit Tests

```bash
# Django tests
docker-compose exec django_web python manage.py test

# Flask tests (si existen)
docker-compose exec flask_reports pytest tests/
```

### Health Checks

```bash
# Nginx gateway
curl http://localhost/health

# Django backend
curl http://localhost:8000/
curl http://localhost/admin/

# Flask microservicio
curl http://localhost:5000/health
curl http://localhost:5000/api/v2/reportes/resumen-transacciones
```

### Ejemplo: Test del API Gateway

```bash
# Debe enrutar a Django
curl http://localhost/api/v1/planes/
→ {"planes": [...]}

# Debe enrutar a Flask
curl http://localhost/api/v2/reportes/resumen-transacciones
→ {"resumen": {...}}
```

---

## 📝 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz (opcional):

```env
# Django
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Flask
FLASK_ENV=production
FLASK_PORT=5000

# Database
DATABASE_URL=sqlite:///db.sqlite3
```

### Docker-Compose Overrides

Para desarrollo local, crear `docker-compose.override.yml`:

```yaml
version: '3.9'

services:
  django_web:
    environment:
      - DEBUG=True
    ports:
      - "8000:8000"

  flask_reports:
    environment:
      - FLASK_DEBUG=True
    ports:
      - "5000:5000"
```

---

## 🐛 Troubleshooting

### Puerto 80 en uso
```bash
# Linux/Mac
sudo lsof -i :80
kill -9 <PID>

# Windows (PowerShell admin)
Get-NetTCPConnection -LocalPort 80 | Select-Object OwningProcess
Stop-Process -Id <PID> -Force
```

### Permisos en BD
```bash
docker-compose exec django_web python manage.py migrate
docker-compose exec django_web python manage.py createsuperuser
```

### Logs de errores
```bash
# Ver logs de Nginx
docker-compose logs -f nginx

# Ver logs de Django
docker-compose logs -f django_web

# Ver logs de Flask
docker-compose logs -f flask_reports

# Ver todo
docker-compose logs -f
```

### Rebuild completo
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## 📚 Documentación

- **DECISION_MATRIX.md**: Justificación de la selección del módulo a estrangular
- **WIKI_STRANGLER_PATTERN.md**: Documentación completa para GitHub Wiki
- Código comentado en `reports_service/app.py` y `nginx.conf`

---

## 🔄 Próximos Pasos

### Fase 2: Integración Real con BD
- [ ] Conectar Flask directamente a SQLite compartida
- [ ] Implementar caché Redis para reportes
- [ ] Autenticación entre servicios (JWT/OAuth)

### Fase 3: Event-Driven
- [ ] Publicar eventos de Django a message queue (Kafka/RabbitMQ)
- [ ] Flask consume eventos para actualizaciones en tiempo real

### Fase 4: Full Microservices
- [ ] Migrar más módulos a microservicios
- [ ] Service discovery (Consul/Eureka)
- [ ] Circuit breaker pattern

---

## 📋 Checklist de Entrega

- ✅ Matriz de Decisión (justificación)
- ✅ Microservicio Flask (5 endpoints de reportes)
- ✅ Dockerfile para Django y Flask
- ✅ docker-compose.yml (3 servicios)
- ✅ nginx.conf (strangler routing)
- ✅ Documentación Wiki (MARKDOWN para GitHub)
- ✅ Tests y health checks funcionales
- ✅ Git commit semántico y ordenado

---

## 🎓 Créditos

**Curso**: Arquitectura de Software 2026
**Profesor**: Nicolás Ramírez Vélez
**Taller**: 02 - Patrón Estrangulador
**Equipo**: UniversalGamePass

---

**Última actualización**: 2026-04-13  
**Estado**: ✅ Listo para Producción
