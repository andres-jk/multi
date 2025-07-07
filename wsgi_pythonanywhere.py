"""
WSGI config for multiandamios project en PythonAnywhere.
"""

import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/TUUSUARIO/multi'  # Cambia TUUSUARIO por tu usuario
if path not in sys.path:
    sys.path.append(path)

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
