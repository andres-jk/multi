#!/bin/bash
# COMANDOS PARA EJECUTAR EN PYTHONANYWHERE

echo "=== ACTUALIZACIÓN DE CÓDIGO ==="
cd /home/tu-usuario/multiandamios
git pull origin main

echo "=== CARGA DE DATOS DIVIPOLA ==="
python3.10 cargar_divipola_produccion.py

echo "=== VERIFICACIÓN DE API ==="
python3.10 verificar_api_divipola.py

echo "=== COLECCIÓN DE ARCHIVOS ESTÁTICOS ==="
python3.10 manage.py collectstatic --clear --noinput

echo "=== MIGRACIONES ==="
python3.10 manage.py makemigrations
python3.10 manage.py migrate

echo "=== PROCESO COMPLETADO ==="
echo "RECUERDA:"
echo "1. Hacer 'Reload' en la pestana Web de PythonAnywhere"
echo "2. Probar el sitio web en el navegador"
echo "3. Verificar proceso de pedidos con departamentos/municipios"
