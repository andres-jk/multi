#!/bin/bash

# Script para actualizar el servidor PythonAnywhere con todos los cambios
# Ejecutar este script en la consola Bash de PythonAnywhere

echo "🚀 ACTUALIZANDO MULTIANDAMIOS EN SERVIDOR..."
echo "=============================================="

# 1. Ir al directorio del proyecto
cd ~/multiandamios.pythonanywhere.com || cd ~/multi
echo "📁 Directorio actual: $(pwd)"

# 2. Hacer pull de los cambios
echo "📥 Descargando cambios desde GitHub..."
git pull origin main

# 3. Instalar/actualizar dependencias si es necesario
echo "📦 Verificando dependencias..."
pip3.10 install --user -r requirements.txt

# 4. Migrar base de datos si hay cambios
echo "🗄️ Aplicando migraciones..."
python3.10 manage.py migrate --noinput

# 5. Recopilar archivos estáticos
echo "🎨 Recopilando archivos estáticos..."
python3.10 manage.py collectstatic --noinput

# 6. Verificar URLs problemáticas
echo "🔍 Verificando URLs de empleados..."
python3.10 manage.py check --deploy

# 7. Mostrar información del estado
echo "📊 Estado del proyecto:"
echo "- Directorio: $(pwd)"
echo "- Última confirmación: $(git log -1 --oneline)"
echo "- Archivos estáticos: $(ls -la static/ | wc -l) archivos"

echo ""
echo "✅ ACTUALIZACIÓN COMPLETADA"
echo "🔄 Ahora debes RECARGAR tu aplicación web en PythonAnywhere:"
echo "   1. Ve a la pestaña 'Web'"
echo "   2. Busca tu aplicación"
echo "   3. Haz clic en 'Reload [tu-app].pythonanywhere.com'"
echo ""
echo "🌐 Después visita: https://dalej.pythonanywhere.com/empleados/"
echo "=============================================="
