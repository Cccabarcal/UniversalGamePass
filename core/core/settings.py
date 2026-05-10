"""
Django settings for core project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-=ms4)px(u60s9^f7+_g=xed6)!s!(e5@0n#hvur*fq(l_1u*fb",
)

DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

# Environment flag used by factories (DEV/PROD)
ENV_TYPE = os.getenv("ENV_TYPE", "DEV")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [
    o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database (sqlite por default, postgres si se inyecta DATABASE_URL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# Internationalization (i18n) - Bilingue ES/EN via gettext
# ============================================================================
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', 'Espanol'),
    ('en', 'English'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ============================================================================
# Celery + Redis (broker asincrono)
# ============================================================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ============================================================================
# Servicios externos: API de terceros (Adapter) y endpoint de equipo aliado
# ============================================================================
THIRD_PARTY_GAMES_API_URL = os.getenv(
    "THIRD_PARTY_GAMES_API_URL",
    "https://www.freetogame.com/api/games",
)
ALLY_API_URL = os.getenv("ALLY_API_URL", "")  # URL del equipo aliado (configurable)
ALLY_API_TIMEOUT = int(os.getenv("ALLY_API_TIMEOUT", "5"))

# Identidad del sistema (Servicio a Proveer)
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "UniversalGamePass")
SYSTEM_VERSION = os.getenv("SYSTEM_VERSION", "2.0.0")
