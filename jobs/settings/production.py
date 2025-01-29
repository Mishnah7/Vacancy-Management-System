import os
import sys
import dj_database_url
from .base import *

# Ensure we're in production environment
if 'RAILWAY_ENVIRONMENT' not in os.environ:
    print("Error: Production settings loaded but RAILWAY_ENVIRONMENT not found.")
    print("If you're running locally, use: python manage.py runserver --settings=jobs.settings.local")
    sys.exit(1)

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    print("Error: DJANGO_SECRET_KEY environment variable is required in production")
    sys.exit(1)

# Configure allowed hosts
ALLOWED_HOSTS = [
    'vacancy-management-system-production.up.railway.app',
    '.up.railway.app',  # Allow all Railway subdomains
    'localhost',
    '127.0.0.1',
]

# Database configuration for Railway
# Construct internal database URL to avoid egress fees
PGUSER = os.environ.get('PGUSER')
PGPASSWORD = os.environ.get('POSTGRES_PASSWORD')
PGHOST = os.environ.get('PGHOST')
PGPORT = os.environ.get('PGPORT')
PGDATABASE = os.environ.get('PGDATABASE')

if all([PGUSER, PGPASSWORD, PGHOST, PGPORT, PGDATABASE]):
    database_url = f'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'
else:
    # Fallback to DATABASE_URL if any of the components are missing
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Error: Neither internal PostgreSQL variables nor DATABASE_URL are properly set")
        sys.exit(1)

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=60,  # Reduced from 600 to improve reliability
        conn_health_checks=True,
        engine='django.db.backends.postgresql'
    )
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Security settings - make them configurable
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('DJANGO_SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('DJANGO_CSRF_COOKIE_SECURE', 'True') == 'True'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://vacancy-management-system-production.up.railway.app',
    'https://*.up.railway.app',  # Allow all Railway subdomains
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ensure MIDDLEWARE has WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware') 