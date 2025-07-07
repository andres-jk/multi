# =================================================================
# CONFIGURACIÓN ESPECÍFICA PARA USUARIO: dalej
# Copiar y pegar al FINAL del archivo multiandamios/settings.py
# =================================================================

# Hosts permitidos - CONFIGURACIÓN ESPECÍFICA PARA dalej
ALLOWED_HOSTS = [
    'dalej.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = '/home/dalej/multi/staticfiles'

# Configuración de archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/dalej/multi/media'

# Base de datos con ruta absoluta
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/dalej/multi/db.sqlite3',
    }
}

# Para testing inicial, mantener DEBUG = True
DEBUG = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://dalej.pythonanywhere.com',
]

# Configuraciones de seguridad desactivadas para testing
# SECURE_SSL_REDIRECT = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

print("✅ Configuración de PythonAnywhere cargada para usuario: dalej")
print("🌐 Dominio: dalej.pythonanywhere.com")
