"""
WSGI config for multiandamios project en PythonAnywhere.
Configuración específica para usuario: dalej
"""

import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/dalej/multi'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
