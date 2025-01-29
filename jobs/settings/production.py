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
ALLOWED_HOSTS = ['*']  # Temporarily allow all hosts for debugging

# Print all environment variables for debugging
print("Available environment variables:")
for key, value in os.environ.items():
    if any(db_key in key.lower() for db_key in ['database', 'db', 'postgres', 'sql']):
        print(f"{key}: {'*' * len(value)}")  # Mask the actual values for security

# Database configuration for Railway
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    # Try to construct from individual components
    db_components = {
        'user': os.environ.get('PGUSER') or os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('PGPASSWORD') or os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('PGHOST') or os.environ.get('RAILWAY_PRIVATE_DOMAIN'),
        'port': os.environ.get('PGPORT', '5432'),
        'name': os.environ.get('PGDATABASE') or os.environ.get('POSTGRES_DB', 'railway')
    }
    
    # Print available components (masking sensitive data)
    print("\nDatabase components found:")
    for key, value in db_components.items():
        if value:
            if key in ['password']:
                print(f"{key}: {'*' * len(value)}")
            else:
                print(f"{key}: {value}")
        else:
            print(f"{key}: NOT FOUND")

    if all(db_components.values()):
        database_url = f"postgresql://{db_components['user']}:{db_components['password']}@{db_components['host']}:{db_components['port']}/{db_components['name']}"
        print("\nSuccessfully constructed database URL")
    else:
        missing = [k for k, v in db_components.items() if not v]
        print(f"\nError: Missing database components: {', '.join(missing)}")
        sys.exit(1)

print("\nAttempting to configure database with URL...")
DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=60,
        conn_health_checks=True,
        engine='django.db.backends.postgresql'
    )
}
print("Database configuration completed")

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Security settings
SECURE_SSL_REDIRECT = False  # Temporarily disable for debugging
SESSION_COOKIE_SECURE = False  # Temporarily disable for debugging
CSRF_COOKIE_SECURE = False  # Temporarily disable for debugging
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',  # Allow all Railway subdomains
    'http://*.railway.app',   # Temporarily allow HTTP for debugging
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
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
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Set to DEBUG to see more details
            'propagate': False,
        },
        'gunicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.error': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ensure MIDDLEWARE has WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware') 