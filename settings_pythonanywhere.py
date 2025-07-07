# Configuraciones adicionales para PythonAnywhere
# Agregar estas líneas al final de settings.py

# PythonAnywhere specific settings
ALLOWED_HOSTS = [
    'tuusuario.pythonanywhere.com',  # Cambia por tu dominio
    'localhost',
    '127.0.0.1',
]

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = '/home/tuusuario/multi/staticfiles'  # Cambia tuusuario

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/tuusuario/multi/media'  # Cambia tuusuario

# Database configuration (mantener SQLite para pruebas)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security settings for production
DEBUG = False  # Cambiar a False en producción
SECRET_KEY = 'tu-secret-key-aqui'  # Cambiar por una clave segura

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://tuusuario.pythonanywhere.com',  # Cambia por tu dominio
]
