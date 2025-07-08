#!/bin/bash
# Script de actualización completa para PythonAnywhere
# Ejecutar en la consola bash de PythonAnywhere

echo "🚀 Iniciando actualización completa del proyecto MultiAndamios..."

# 1. Navegar al directorio del proyecto
cd ~/multiandamios
echo "📁 Directorio actual: $(pwd)"

# 2. Actualizar código desde GitHub
echo "📥 Descargando últimas actualizaciones..."
git pull origin main

# 3. Verificar que usuarios/forms.py tiene EmpleadoForm
echo "🔍 Verificando EmpleadoForm..."
if grep -q "class EmpleadoForm" usuarios/forms.py; then
    echo "✅ EmpleadoForm encontrada en usuarios/forms.py"
else
    echo "❌ EmpleadoForm NO encontrada, ejecutando corrección..."
    python3 fix_empleado_form.py
fi

# 4. Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
pip3.10 install --user -r requirements.txt

# 5. Ejecutar migraciones
echo "🗃️ Aplicando migraciones..."
python3.10 manage.py makemigrations
python3.10 manage.py migrate

# 6. Recopilar archivos estáticos
echo "📂 Recopilando archivos estáticos..."
python3.10 manage.py collectstatic --noinput

# 7. Verificar la configuración
echo "🔧 Verificando configuración..."
python3.10 manage.py check

# 8. Verificar que EmpleadoForm es importable
echo "🧪 Probando importación de EmpleadoForm..."
python3.10 -c "
try:
    from usuarios.forms import EmpleadoForm
    print('✅ EmpleadoForm se importa correctamente')
except ImportError as e:
    print(f'❌ Error al importar EmpleadoForm: {e}')
    exit(1)
"

echo "✅ Actualización completada"
echo ""
echo "📋 Pasos finales:"
echo "1. Ve a la pestaña 'Web' en PythonAnywhere"
echo "2. Haz clic en 'Reload andresjaramillo.pythonanywhere.com'"
echo "3. Espera a que se recargue completamente"
echo "4. Prueba acceder a la gestión de empleados"
echo ""
echo "🌐 URL de prueba: https://andresjaramillo.pythonanywhere.com/usuarios/empleados/"
