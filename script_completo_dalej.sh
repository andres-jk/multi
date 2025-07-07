#!/bin/bash
# SCRIPT COMPLETO PARA DALEJ - SOLUCIÓN ALLOWED_HOSTS + DIVIPOLA

echo "=== SOLUCIONANDO ERROR ALLOWED_HOSTS + DIVIPOLA ==="

echo "PASO 1: Configurar ALLOWED_HOSTS"
echo "DEBES EDITAR MANUALMENTE:"
echo "nano multiandamios/settings.py"
echo ""
echo "Buscar ALLOWED_HOSTS y cambiar a:"
echo "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"
echo ""
echo "Presiona Enter cuando hayas terminado de editar settings.py..."
read

echo "PASO 2: Respaldar base de datos"
cp db.sqlite3 db.sqlite3.backup

echo "PASO 3: Actualizar código"
git reset --hard origin/main

echo "PASO 4: Verificar archivos DIVIPOLA"
ls -la | grep divipola

echo "PASO 5: Cargar datos DIVIPOLA"
python3.10 cargar_divipola_produccion.py

echo "PASO 6: Verificar API"
python3.10 verificar_api_divipola.py

echo "PASO 7: Actualizar archivos estáticos"
python3.10 manage.py collectstatic --clear --noinput

echo "=== PROCESO COMPLETADO ==="
echo "AHORA DEBES:"
echo "1. Ir a la pestaña 'Web' en PythonAnywhere"
echo "2. Hacer clic en 'Reload'"
echo "3. Probar tu sitio: https://dalej.pythonanywhere.com/checkout/"
echo ""
echo "¡El problema debe estar resuelto!"
