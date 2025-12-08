# sgtr/settings.py - Configuración mejorada con seguridad ISO 27001
"""
Django settings for sgtr project.

Configuración optimizada con:
- Seguridad según ISO 27001
- Soporte dual SQLite/PostgreSQL
- Variables de entorno
- Configuración separada dev/prod
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    # Continuar sin .env, usar variables de entorno del sistema

# ==============================================================================
# SEGURIDAD - ISO 27001 Compliance
# ==============================================================================

# SECURITY WARNING: don't run with debug turned on in production!
# ISO 27001: A.12.4.1 - Event logging
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
# ISO 27001: A.9.4.3 - Password management system
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        # Clave insegura SOLO para desarrollo local
        SECRET_KEY = 'django-insecure-dev-key-do-not-use-in-production'
    else:
        # En producción es OBLIGATORIO usar variable de entorno
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured("La variable de entorno SECRET_KEY es obligatoria en producción.")

# ISO 27001: A.13.1.3 - Segregation in networks
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ISO 27001: A.13.1.1 - Network controls
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.ngrok-free.app'
).split(',')

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD HTTPS (Producción)
# ISO 27001: A.13.1.3 - Segregation in networks
# ==============================================================================

if not DEBUG:
    # Forzar HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Seguridad adicional
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Proxy headers (para Nginx/Apache)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ==============================================================================
# APLICACIONES
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Mis aplicaciones
    'usuarios',
    'inventario',
    'tickets',
    # Apps de terceros
    'crispy_forms',
    'crispy_bootstrap5',
    'django_htmx',
]

# ==============================================================================
# MIDDLEWARE
# ISO 27001: A.14.1.2 - Securing application services
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sgtr.urls'

# ==============================================================================
# TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sgtr.wsgi.application'

# ==============================================================================
# BASE DE DATOS - Configuración Dual SQLite/PostgreSQL
# ISO 27001: A.12.3.1 - Information backup
# ==============================================================================

# Detectar si hay DATABASE_URL (Docker/Producción con PostgreSQL)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Usar PostgreSQL desde variable de entorno (Docker/Producción)
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    # Usar SQLite para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            # Optimizaciones para SQLite
            'OPTIONS': {
                'timeout': 20,
                'init_command': "PRAGMA foreign_keys=ON;",
            }
        }
    }

# Configuración de conexión para PostgreSQL
if DATABASE_URL and 'postgresql' in DATABASE_URL:
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Conexiones persistentes
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
    }

# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ISO 27001: A.9.4.3 - Password management system
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # ISO 27001 recomienda mínimo 8 caracteres
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# CONFIGURACIÓN DE SESIONES
# ISO 27001: A.9.4.2 - Secure log-on procedures
# ==============================================================================

# Expiración de sesión por inactividad (30 minutos)
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Seguridad de cookies
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# INTERNACIONALIZACIÓN
# ==============================================================================

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Archivos media (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# CONFIGURACIÓN DE CACHÉ
# ISO 27001: A.12.6.1 - Management of technical vulnerabilities (Performance)
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sgtr-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Cache para sesiones (opcional, mejora rendimiento)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# ==============================================================================
# LOGGING
# ISO 27001: A.12.4.1 - Event logging
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'tickets': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# ==============================================================================
# EMAIL
# ISO 27001: A.13.2.1 - Information transfer policies and procedures
# ==============================================================================

# Configuración de email (desarrollo: consola, producción: SMTP)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = os.environ.get(
        'EMAIL_BACKEND',
        'django.core.mail.backends.smtp.EmailBackend'
    )
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# ==============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==============================================================================

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Autenticación
LOGIN_URL = '/cuentas/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/landing/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# CONFIGURACIÓN DE DESARROLLO
# ==============================================================================

if DEBUG:
    # Permitir todos los hosts en desarrollo
    ALLOWED_HOSTS = ['*']
    
    # Deshabilitar algunas restricciones de seguridad en desarrollo
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    
    # Mostrar más información en errores
    INTERNAL_IPS = ['127.0.0.1', 'localhost']