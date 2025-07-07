# wsgi.py COMPLETO para PythonAnywhere
# Copia TODO este contenido y reemplaza completamente tu wsgi.py

import os
import sys

# Add your project directory to the sys.path
path = '/home/Dalej/multi'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
