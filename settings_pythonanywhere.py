# Configuraciones adicionales para PythonAnywhere
# Agregar estas líneas al final de settings.py

import os
from pathlib import Path

# Definir BASE_DIR si no está definido
BASE_DIR = Path(__file__).resolve().parent.parent

# PythonAnywhere specific settings
ALLOWED_HOSTS = [
    'tuusuario.pythonanywhere.com',  # Cambia por tu dominio real
    'localhost',
    '127.0.0.1',
]

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = '/home/tuusuario/multi/staticfiles'  # Cambia tuusuario por tu usuario real

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/tuusuario/multi/media'  # Cambia tuusuario por tu usuario real

# Database configuration (usar ruta absoluta para PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/tuusuario/multi/db.sqlite3',  # Ruta absoluta para PythonAnywhere
    }
}

# Security settings for production
DEBUG = False  # IMPORTANTE: Cambiar a False en producción
SECRET_KEY = 'django-insecure-CAMBIA-ESTA-CLAVE-POR-UNA-SEGURA'  # IMPORTANTE: Cambiar por una clave segura

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://tuusuario.pythonanywhere.com',  # Cambia por tu dominio real
]

# Configuraciones adicionales para PythonAnywhere
SECURE_SSL_REDIRECT = True  # Forzar HTTPS en producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
