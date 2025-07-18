#!/bin/bash
# Script completo para desplegar MultiAndamios en PythonAnywhere
# Ejecutar este script en la consola Bash de PythonAnywhere

echo "🚀 DESPLEGANDO MULTIANDAMIOS EN PYTHONANYWHERE"
echo "=============================================="

# 1. Ir al directorio correcto (ajustar según tu configuración)
echo "📁 Navegando al directorio del proyecto..."
cd ~
if [ -d "multi" ]; then
    cd multi
    echo "✅ Usando directorio existente: ~/multi"
elif [ -d "multiandamios" ]; then
    cd multiandamios
    echo "✅ Usando directorio existente: ~/multiandamios"
else
    echo "📥 Clonando repositorio desde GitHub..."
    git clone https://github.com/andres-jk/multi.git
    cd multi
fi

echo "📍 Directorio actual: $(pwd)"

# 2. Actualizar desde GitHub
echo ""
echo "📥 Actualizando desde GitHub..."
git fetch origin
git reset --hard origin/main
echo "✅ Código actualizado desde GitHub"

# 3. Configurar entorno virtual
echo ""
echo "🐍 Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

source venv/bin/activate
echo "✅ Entorno virtual activado"

# 4. Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install django==4.2.23
pip install reportlab>=4.0.0
pip install pillow>=10.0.0
echo "✅ Dependencias instaladas"

# 5. Configurar settings para producción
echo ""
echo "⚙️ Configurando settings para producción..."
cat > multiandamios/settings_production.py << 'EOF'
from .settings import *

# Configuración para PythonAnywhere
DEBUG = False

# Hosts permitidos - AJUSTAR según tu dominio de PythonAnywhere
ALLOWED_HOSTS = [
    'dalej.pythonanywhere.com',
    'www.dalej.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Archivos de media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Seguridad para producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
EOF

echo "✅ Settings de producción configurados"

# 6. Aplicar migraciones
echo ""
echo "🗃️ Aplicando migraciones..."
python manage.py migrate --settings=multiandamios.settings_production
echo "✅ Migraciones aplicadas"

# 7. Recopilar archivos estáticos
echo ""
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
echo "✅ Archivos estáticos recopilados"

# 8. Crear superusuario si no existe
echo ""
echo "👤 Configurando superusuario..."
python manage.py shell --settings=multiandamios.settings_production << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@multiandamios.com',
        password='admin123',
        rol='admin'
    )
    print("✅ Superusuario 'admin' creado con contraseña 'admin123'")
else:
    print("✅ Superusuario ya existe")
EOF

# 9. Configurar WSGI
echo ""
echo "🌐 Configurando WSGI..."
cat > wsgi.py << 'EOF'
import os
import sys

# Agregar el directorio del proyecto al path
project_home = '/home/dalej/multi'  # AJUSTAR según tu usuario
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'multiandamios.settings_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF

echo "✅ WSGI configurado"

# 10. Verificar funcionamiento
echo ""
echo "🔍 Verificando funcionamiento..."
python manage.py check --settings=multiandamios.settings_production

# 11. Mostrar resumen final
echo ""
echo "🎉 DESPLIEGUE COMPLETADO"
echo "========================"
echo "✅ Código actualizado desde GitHub"
echo "✅ Entorno virtual configurado"
echo "✅ Dependencias instaladas"
echo "✅ Settings de producción configurados"
echo "✅ Migraciones aplicadas"
echo "✅ Archivos estáticos recopilados"
echo "✅ Superusuario configurado"
echo "✅ WSGI configurado"
echo ""
echo "📋 CONFIGURACIÓN MANUAL NECESARIA:"
echo "1. En la pestaña Web de PythonAnywhere:"
echo "   - Source code: /home/dalej/multi"
echo "   - Working directory: /home/dalej/multi"
echo "   - WSGI configuration file: /home/dalej/multi/wsgi.py"
echo ""
echo "2. En la sección Static files:"
echo "   - URL: /static/"
echo "   - Directory: /home/dalej/multi/staticfiles"
echo ""
echo "3. En la sección Static files (media):"
echo "   - URL: /media/"
echo "   - Directory: /home/dalej/multi/media"
echo ""
echo "4. Recargar la aplicación web"
echo ""
echo "🔐 CREDENCIALES DE ACCESO:"
echo "Usuario admin: admin"
echo "Contraseña: admin123"
echo ""
echo "🌐 Tu aplicación estará disponible en:"
echo "https://dalej.pythonanywhere.com"
echo ""
echo "¡DESPLIEGUE COMPLETADO CON ÉXITO! 🚀"
