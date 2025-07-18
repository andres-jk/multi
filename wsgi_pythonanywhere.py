"""
Configuración WSGI para MultiAndamios en PythonAnywhere
Este archivo debe copiarse a /var/www/dalej_pythonanywhere_com_wsgi.py
"""

import os
import sys

# Configurar el path del proyecto
# IMPORTANTE: Cambiar 'dalej' por tu nombre de usuario de PythonAnywhere
project_home = '/home/dalej/multi'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activar el entorno virtual
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings_production')

# Importar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
