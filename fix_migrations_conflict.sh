#!/bin/bash

echo "=== SOLUCIONANDO CONFLICTO DE MIGRACIONES ==="
echo "Resolviendo: Conflicting migrations detected in usuarios app"
echo

# Verificar si estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "Error: No se encuentra manage.py"
    echo "Ejecuta este script desde el directorio del proyecto: cd ~/multi"
    exit 1
fi

echo "1. Creando migración de merge para resolver conflictos..."
python manage.py makemigrations --merge usuarios --settings=multiandamios.settings_production

echo

echo "2. Aplicando todas las migraciones..."
python manage.py migrate --settings=multiandamios.settings_production

echo

echo "3. Verificando estado de migraciones..."
python manage.py showmigrations usuarios --settings=multiandamios.settings_production

echo

echo "4. Recolectando archivos estáticos nuevamente..."
python manage.py collectstatic --noinput --settings=multiandamios.settings_production

echo

echo "=== MIGRACIONES SOLUCIONADAS ==="
echo
echo "SIGUIENTES PASOS:"
echo "1. Ve a tu panel de PythonAnywhere: https://www.pythonanywhere.com/user/dalej/"
echo "2. Navega a la pestaña 'Web'"
echo "3. Haz click en 'Reload dalej.pythonanywhere.com'"
echo "4. Prueba tu sitio: https://dalej.pythonanywhere.com"
echo
echo "¡Las migraciones conflictivas han sido resueltas!"
