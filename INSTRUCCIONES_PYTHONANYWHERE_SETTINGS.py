"""
Configuración específica para PythonAnywhere
============================================

INSTRUCCIONES DE USO:
1. Copia el contenido de este archivo
2. Pégalo al FINAL del archivo multiandamios/settings.py
3. Personaliza las configuraciones marcadas con "CAMBIAR"

IMPORTANTE: Asegúrate de cambiar:
- 'tuusuario' por tu nombre de usuario real de PythonAnywhere
- La SECRET_KEY por una clave segura
- DEBUG a False para producción
"""

# ====================================================================
# CONFIGURACIONES PARA PYTHONANYWHERE - COPIAR AL FINAL DE SETTINGS.PY
# ====================================================================

# Hosts permitidos (CAMBIAR tuusuario por tu usuario real)
ALLOWED_HOSTS = [
    'tuusuario.pythonanywhere.com',  # CAMBIAR: tu dominio de PythonAnywhere
    'localhost',
    '127.0.0.1',
]

# Configuración de archivos estáticos para producción
STATIC_URL = '/static/'
STATIC_ROOT = '/home/tuusuario/multi/staticfiles'  # CAMBIAR: tu usuario

# Configuración de archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/tuusuario/multi/media'  # CAMBIAR: tu usuario

# Base de datos con ruta absoluta (CAMBIAR tuusuario)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/tuusuario/multi/db.sqlite3',  # CAMBIAR: tu usuario
    }
}

# Configuraciones de seguridad para producción
DEBUG = False  # IMPORTANTE: False en producción, True solo para debugging

# Clave secreta (CAMBIAR por una clave segura y única)
SECRET_KEY = 'django-insecure-GENERAR-UNA-CLAVE-SEGURA-AQUI'

# Configuraciones CSRF (CAMBIAR tuusuario)
CSRF_TRUSTED_ORIGINS = [
    'https://tuusuario.pythonanywhere.com',  # CAMBIAR: tu dominio
]

# Configuraciones adicionales de seguridad
SECURE_SSL_REDIRECT = True  # Forzar HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ====================================================================
# FIN DE CONFIGURACIONES PARA PYTHONANYWHERE
# ====================================================================
