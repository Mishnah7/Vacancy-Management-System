import os
import sys
import dj_database_url
from .base import *

# Ensure we're in production environment
if 'RAILWAY_ENVIRONMENT' not in os.environ:
    print("Error: Production settings loaded but RAILWAY_ENVIRONMENT not found.")
    print("If you're running locally, use: python manage.py runserver --settings=jobs.settings.local")
    sys.exit(1)

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    print("Error: DJANGO_SECRET_KEY environment variable is required in production")
    sys.exit(1)

# Configure allowed hosts
ALLOWED_HOSTS = [
    '.railway.app',
    'localhost',
    '127.0.0.1',
    '*',  # Temporarily allow all hosts
]

# Print all environment variables for debugging
print("Available environment variables:")
for key, value in os.environ.items():
    if any(db_key in key.lower() for db_key in ['database', 'db', 'postgres', 'sql']):
        print(f"{key}: {'*' * len(value)}")  # Mask the actual values for security

# Database configuration for Railway
print("\nChecking database configuration...")

# First try DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("Error: DATABASE_URL environment variable is required")
    sys.exit(1)

print("Configuring database connection...")
DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=60,
        conn_health_checks=True,
    )
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Security settings (temporarily disabled for debugging)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'http://*.railway.app',
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(name)s:%(lineno)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Ensure MIDDLEWARE has WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware') 