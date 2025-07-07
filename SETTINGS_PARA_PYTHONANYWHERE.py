# =================================================================
# CONFIGURACIONES PARA PYTHONANYWHERE
# Copiar y pegar al FINAL del archivo multiandamios/settings.py
# =================================================================

import os

# Obtener el nombre de usuario automáticamente
USERNAME = os.environ.get('USER', 'tuusuario')

# Hosts permitidos (cambiar tuusuario por tu usuario real)
ALLOWED_HOSTS = [
    f'{USERNAME}.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = f'/home/{USERNAME}/multi/staticfiles'

# Configuración de archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = f'/home/{USERNAME}/multi/media'

# Base de datos con ruta absoluta
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f'/home/{USERNAME}/multi/db.sqlite3',
    }
}

# Para testing inicial, mantener DEBUG = True
# Cambiar a False cuando todo funcione
DEBUG = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    f'https://{USERNAME}.pythonanywhere.com',
]

# Desactivar configuraciones de seguridad para testing inicial
# Activar cuando todo funcione correctamente
# SECURE_SSL_REDIRECT = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

print(f"PythonAnywhere configurado para usuario: {USERNAME}")
print(f"Dominio: {USERNAME}.pythonanywhere.com")
