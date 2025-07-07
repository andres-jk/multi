#!/bin/bash
# Script para actualizar el repositorio multi en PythonAnywhere
# Ejecutar línea por línea en la consola Bash de PythonAnywhere

echo "=== ACTUALIZANDO REPOSITORIO MULTI ==="
echo "Repositorio: https://github.com/andres-jk/multi.git"
echo "Ruta: /home/TU-USUARIO/multi"
echo

echo "1. Navegando al repositorio..."
cd /home/TU-USUARIO/multi

echo "2. Verificando estado del repositorio..."
git status

echo "3. Actualizando código desde GitHub..."
git pull origin main

echo "4. Verificando que los archivos se descargaron..."
ls -la cargar_divipola_produccion.py
ls -la verificar_api_divipola.py
ls -la test_divipola_completo.py

echo "5. Cargando datos de DIVIPOLA..."
python3.10 cargar_divipola_produccion.py

echo "6. Verificando API de DIVIPOLA..."
python3.10 verificar_api_divipola.py

echo "7. Ejecutando tests completos..."
python3.10 test_divipola_completo.py

echo "8. Actualizando archivos estáticos..."
python3.10 manage.py collectstatic --clear --noinput

echo "=== PROCESO COMPLETADO ==="
echo "AHORA DEBES:"
echo "1. Ir a la pestaña 'Web' en PythonAnywhere"
echo "2. Hacer clic en 'Reload' para reiniciar la aplicación"
echo "3. Probar el sitio web y verificar que funcione el checkout"
echo
echo "El problema de departamentos y municipios debe estar solucionado."
