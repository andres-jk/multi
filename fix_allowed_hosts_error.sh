#!/bin/bash

echo "=== SOLUCIÓN RÁPIDA: ALLOWED_HOSTS ERROR ==="
echo "Solucionando error: DisallowedHost dalej.pythonanywhere.com"
echo

# Verificar si estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "Error: No se encuentra manage.py"
    echo "Ejecuta este script desde el directorio del proyecto: cd ~/multi"
    exit 1
fi

echo "1. Verificando configuración actual..."

# Verificar ALLOWED_HOSTS en settings_production.py
if grep -q "dalej.pythonanywhere.com" multiandamios/settings_production.py; then
    echo "   ✓ dalej.pythonanywhere.com ya está en settings_production.py"
else
    echo "   ⚠ Agregando dalej.pythonanywhere.com a settings_production.py"
    
    # Backup del archivo
    cp multiandamios/settings_production.py multiandamios/settings_production.py.bak
    
    # Agregar el host
    sed -i "/ALLOWED_HOSTS = \[/,/\]/s/\]/    'dalej.pythonanywhere.com',\n    'www.dalej.pythonanywhere.com',\n\]/" multiandamios/settings_production.py
fi

echo

echo "2. Verificando archivo WSGI..."
WSGI_FILE="/var/www/dalej_pythonanywhere_com_wsgi.py"

if [ ! -f "$WSGI_FILE" ]; then
    echo "   ⚠ Creando archivo WSGI en $WSGI_FILE"
    
    cat > "$WSGI_FILE" << 'EOL'
import os
import sys

# Configurar el path del proyecto
project_home = '/home/dalej/multi'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activar el entorno virtual
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Configurar Django para usar settings de producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings_production')

# Importar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOL
    
    echo "   ✓ Archivo WSGI creado"
else
    echo "   ✓ Archivo WSGI ya existe"
    
    # Verificar que use settings_production
    if grep -q "settings_production" "$WSGI_FILE"; then
        echo "   ✓ WSGI configurado correctamente para production"
    else
        echo "   ⚠ Actualizando WSGI para usar settings_production"
        sed -i "s/multiandamios.settings/multiandamios.settings_production/g" "$WSGI_FILE"
    fi
fi

echo

echo "3. Aplicando migraciones con settings de producción..."
python manage.py migrate --settings=multiandamios.settings_production

echo

echo "4. Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --settings=multiandamios.settings_production

echo

echo "=== CONFIGURACIÓN COMPLETADA ==="
echo
echo "SIGUIENTES PASOS:"
echo "1. Ve a tu panel de PythonAnywhere: https://www.pythonanywhere.com/user/dalej/"
echo "2. Navega a la pestaña 'Web'"
echo "3. Haz click en 'Reload dalej.pythonanywhere.com'"
echo "4. Espera unos segundos y prueba tu sitio: https://dalej.pythonanywhere.com"
echo
echo "Si el problema persiste:"
echo "- Revisa los logs de error en PythonAnywhere > Web > Log files"
echo "- Verifica que el archivo WSGI apunte al directorio correcto"
echo "- Asegúrate de que el entorno virtual esté activado"
echo

echo "CONFIGURACIÓN ACTUAL:"
echo "- Proyecto: /home/dalej/multi"
echo "- WSGI: /var/www/dalej_pythonanywhere_com_wsgi.py"
echo "- Settings: multiandamios.settings_production"
echo "- Allowed Hosts: dalej.pythonanywhere.com, www.dalej.pythonanywhere.com"
echo

echo "¡Listo! Tu aplicación debería funcionar ahora."
