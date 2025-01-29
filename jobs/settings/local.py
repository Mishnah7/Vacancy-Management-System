from .base import *
import os

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Security settings - for development only
SECRET_KEY = 'django-insecure-development-key-for-local-use-only'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Remove Elasticsearch for local development
if 'django_elasticsearch_dsl' in INSTALLED_APPS:
    INSTALLED_APPS.remove('django_elasticsearch_dsl')
ELASTICSEARCH_DSL_AUTOSYNC = False

# Prometheus settings
ENABLE_PROMETHEUS = False

# Session settings
SESSION_COOKIE_AGE = 60 * 60 * 24  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Email settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable security settings for local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False 