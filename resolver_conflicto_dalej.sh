#!/bin/bash
# Script para resolver conflicto de merge y cargar DIVIPOLA
# Ejecutar línea por línea en PythonAnywhere

echo "=== RESOLVIENDO CONFLICTO DE MERGE ==="
echo "1. Respaldando base de datos actual..."
cp db.sqlite3 db.sqlite3.backup

echo "2. Haciendo stash de cambios locales..."
git stash

echo "3. Actualizando código desde GitHub..."
git pull origin main

echo "4. Verificando que los archivos se descargaron..."
echo "Archivos de DIVIPOLA:"
ls -la cargar_divipola_produccion.py
ls -la verificar_api_divipola.py
ls -la test_divipola_completo.py

echo "5. Cargando datos de DIVIPOLA..."
python3.10 cargar_divipola_produccion.py

echo "6. Verificando API..."
python3.10 verificar_api_divipola.py

echo "7. Ejecutando tests..."
python3.10 test_divipola_completo.py

echo "8. Actualizando archivos estáticos..."
python3.10 manage.py collectstatic --clear --noinput

echo "=== PROCESO COMPLETADO ==="
echo "AHORA DEBES:"
echo "1. Ir a la pestaña 'Web' en PythonAnywhere"
echo "2. Hacer clic en 'Reload'"
echo "3. Probar el checkout en tu sitio web"
echo
echo "El problema de departamentos y municipios debe estar resuelto."
