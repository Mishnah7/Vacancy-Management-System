from .base import *

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Remove Elasticsearch for local development
if 'django_elasticsearch_dsl' in INSTALLED_APPS:
    INSTALLED_APPS.remove('django_elasticsearch_dsl')
ELASTICSEARCH_DSL_AUTOSYNC = False

# Security settings - for development only
SECRET_KEY = 'django-insecure-development-key-for-local-use-only'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Prometheus settings
ENABLE_PROMETHEUS = False

# Session settings
SESSION_COOKIE_AGE = 60 * 60 * 24  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Email settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 