#!/bin/bash
# Script para desplegar MultiAndamios en PythonAnywhere
# Ejecutar este script en una consola Bash de PythonAnywhere

echo "🚀 DESPLEGANDO MULTIANDAMIOS EN PYTHONANYWHERE"
echo "=============================================="

# Obtener nombre de usuario actual
USERNAME=$(whoami)
echo "👤 Usuario detectado: $USERNAME"

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
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
source venv/bin/activate
echo "✅ Entorno virtual activado"

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Configurando base de datos..."
python manage.py migrate

echo "🔧 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "👤 Creando superusuario (opcional)..."
echo "Si quieres crear un superusuario, ejecuta manualmente:"
echo "python manage.py createsuperuser"

echo ""
echo "✅ DESPLIEGUE COMPLETADO"
echo "======================="
echo "📋 Próximos pasos OBLIGATORIOS:"
echo ""
echo "1. 🌐 Configurar Web App en PythonAnywhere Dashboard:"
echo "   - Ve a 'Web' → 'Add a new web app'"
echo "   - Elige 'Manual configuration' → Python 3.10"
echo ""
echo "2. 📂 Configurar rutas:"
echo "   - Source code: /home/$USERNAME/multi"
echo "   - Virtualenv: /home/$USERNAME/multi/venv"
echo ""
echo "3. ⚙️ Editar archivo WSGI (reemplazar todo el contenido):"
echo "   - Usar el contenido de wsgi_pythonanywhere.py"
echo "   - Cambiar TUUSUARIO por: $USERNAME"
echo ""
echo "4. 🔧 Editar settings.py:"
echo "   - Agregar configuraciones de INSTRUCCIONES_PYTHONANYWHERE_SETTINGS.py"
echo "   - Cambiar 'tuusuario' por: $USERNAME"
echo "   - Cambiar SECRET_KEY por una clave segura"
echo ""
echo "5. 🚀 Hacer Reload de la Web App"
echo ""
echo "🌐 Tu sitio estará en: https://$USERNAME.pythonanywhere.com"
echo ""
echo "🧪 Para probar localmente ejecuta:"
echo "source venv/bin/activate"
echo "python manage.py runserver"
