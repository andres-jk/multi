#!/bin/bash
# Script de una línea para corregir ALLOWED_HOSTS

echo "=== CORRECCIÓN AUTOMÁTICA DE ALLOWED_HOSTS ==="

# Hacer backup del archivo original
cp multiandamios/settings.py multiandamios/settings.py.backup

# Agregar dalej.pythonanywhere.com a ALLOWED_HOSTS
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py

# Si no funcionó el primer comando, probar con otras variantes
sed -i "s/ALLOWED_HOSTS = \['localhost', '127.0.0.1'\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py

# Verificar el cambio
echo "ALLOWED_HOSTS actualizado:"
grep "ALLOWED_HOSTS" multiandamios/settings.py

echo "=== REINICIA LA APLICACIÓN WEB AHORA ==="
echo "Ve a la pestaña 'Web' en PythonAnywhere y haz clic en 'Reload'"
