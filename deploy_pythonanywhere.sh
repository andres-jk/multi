#!/bin/bash
# Script para desplegar MultiAndamios en PythonAnywhere
# Ejecutar este script en una consola Bash de PythonAnywhere

echo "🚀 DESPLEGANDO MULTIANDAMIOS EN PYTHONANYWHERE"
echo "=============================================="

# Verificar si ya existe el proyecto
if [ -d "multi" ]; then
    echo "📁 Proyecto ya existe, actualizando..."
    cd multi
    git pull origin main
    cd ..
else
    echo "📥 Clonando repositorio..."
    git clone https://github.com/andres-jk/multi.git
fi

cd multi

echo "🐍 Configurando entorno virtual..."
# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Configurando base de datos..."
python manage.py migrate

echo "🔧 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ DESPLIEGUE COMPLETADO"
echo "======================="
echo "📋 Próximos pasos:"
echo "1. Configurar Web App en PythonAnywhere Dashboard"
echo "2. Apuntar Source code a: /home/tuusuario/multi"
echo "3. Configurar virtualenv a: /home/tuusuario/multi/venv"
echo "4. Configurar WSGI file"
echo ""
echo "🌐 Para probar localmente ejecuta:"
echo "python manage.py runserver"
