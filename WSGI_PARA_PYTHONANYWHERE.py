"""
WSGI config for multiandamios project en PythonAnywhere.
Copiar este contenido al archivo WSGI de PythonAnywhere.
"""

import os
import sys

# CAMBIAR 'tuusuario' por tu nombre de usuario real de PythonAnywhere
path = '/home/tuusuario/multi'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
