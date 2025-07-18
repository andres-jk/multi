#!/bin/bash

echo "=== DIAGNÓSTICO PYTHONANYWHERE - MULTIANDAMIOS ==="
echo "Fecha: $(date)"
echo

# Verificar configuración del sitio web
echo "1. Verificando configuración del sitio web..."
echo "   - URL del sitio: https://dalej.pythonanywhere.com"
echo "   - Archivo WSGI esperado: /var/www/dalej_pythonanywhere_com_wsgi.py"
echo

# Verificar que el proyecto existe
echo "2. Verificando proyecto..."
if [ -d "/home/dalej/multi" ]; then
    echo "   ✓ Directorio del proyecto encontrado: /home/dalej/multi"
    cd /home/dalej/multi
    
    # Verificar archivos importantes
    if [ -f "manage.py" ]; then
        echo "   ✓ manage.py encontrado"
    else
        echo "   ✗ manage.py NO encontrado"
    fi
    
    if [ -f "multiandamios/settings.py" ]; then
        echo "   ✓ settings.py encontrado"
    else
        echo "   ✗ settings.py NO encontrado"
    fi
    
    if [ -f "multiandamios/settings_production.py" ]; then
        echo "   ✓ settings_production.py encontrado"
    else
        echo "   ✗ settings_production.py NO encontrado"
    fi
else
    echo "   ✗ Directorio del proyecto NO encontrado: /home/dalej/multi"
    echo "   Ejecuta el script de deployment primero"
    exit 1
fi

echo

# Verificar entorno virtual
echo "3. Verificando entorno virtual..."
if [ -d "venv" ]; then
    echo "   ✓ Entorno virtual encontrado"
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Verificar Django
    if python -c "import django; print(f'Django {django.get_version()}')" 2>/dev/null; then
        echo "   ✓ Django instalado correctamente"
    else
        echo "   ✗ Django NO está instalado en el entorno virtual"
    fi
    
else
    echo "   ✗ Entorno virtual NO encontrado"
fi

echo

# Verificar archivo WSGI
echo "4. Verificando archivo WSGI..."
WSGI_FILE="/var/www/dalej_pythonanywhere_com_wsgi.py"
if [ -f "$WSGI_FILE" ]; then
    echo "   ✓ Archivo WSGI encontrado: $WSGI_FILE"
    
    # Verificar contenido del WSGI
    if grep -q "settings_production" "$WSGI_FILE"; then
        echo "   ✓ WSGI configurado para usar settings_production"
    else
        echo "   ⚠ WSGI NO está configurado para usar settings_production"
    fi
else
    echo "   ✗ Archivo WSGI NO encontrado: $WSGI_FILE"
    echo "   Copia el archivo wsgi_pythonanywhere.py al directorio /var/www/"
fi

echo

# Verificar configuración de Django
echo "5. Verificando configuración de Django..."
export DJANGO_SETTINGS_MODULE="multiandamios.settings_production"

# Verificar ALLOWED_HOSTS
python << EOF
try:
    from multiandamios.settings_production import ALLOWED_HOSTS
    print("   ✓ ALLOWED_HOSTS en production:")
    for host in ALLOWED_HOSTS:
        print(f"     - {host}")
    
    if 'dalej.pythonanywhere.com' in ALLOWED_HOSTS:
        print("   ✓ dalej.pythonanywhere.com está en ALLOWED_HOSTS")
    else:
        print("   ✗ dalej.pythonanywhere.com NO está en ALLOWED_HOSTS")
        
except Exception as e:
    print(f"   ✗ Error al cargar settings_production: {e}")
EOF

echo

# Verificar base de datos
echo "6. Verificando base de datos..."
if [ -f "db.sqlite3" ]; then
    echo "   ✓ Base de datos encontrada: db.sqlite3"
    
    # Verificar migraciones
    if python manage.py showmigrations --settings=multiandamios.settings_production | grep -q "\[ \]"; then
        echo "   ⚠ Hay migraciones pendientes"
        echo "   Ejecuta: python manage.py migrate --settings=multiandamios.settings_production"
    else
        echo "   ✓ Migraciones aplicadas"
    fi
else
    echo "   ✗ Base de datos NO encontrada"
fi

echo

# Verificar archivos estáticos
echo "7. Verificando archivos estáticos..."
if [ -d "staticfiles" ]; then
    echo "   ✓ Directorio staticfiles encontrado"
else
    echo "   ✗ Directorio staticfiles NO encontrado"
    echo "   Ejecuta: python manage.py collectstatic --settings=multiandamios.settings_production"
fi

echo

# Comandos de solución rápida
echo "=== COMANDOS DE SOLUCIÓN RÁPIDA ==="
echo
echo "Si hay problemas, ejecuta estos comandos en orden:"
echo
echo "1. Aplicar migraciones:"
echo "   python manage.py migrate --settings=multiandamios.settings_production"
echo
echo "2. Recolectar archivos estáticos:"
echo "   python manage.py collectstatic --noinput --settings=multiandamios.settings_production"
echo
echo "3. Crear superusuario (si es necesario):"
echo "   python manage.py createsuperuser --settings=multiandamios.settings_production"
echo
echo "4. Reiniciar aplicación web:"
echo "   - Ve a pythonanywhere.com > Web"
echo "   - Haz click en 'Reload dalej.pythonanywhere.com'"
echo
echo "5. Verificar logs de error:"
echo "   - Ve a pythonanywhere.com > Web > Log files"
echo "   - Revisa el 'error log' para más detalles"
echo

echo "=== VERIFICACIÓN ADICIONAL ==="
echo "URL de prueba: https://dalej.pythonanywhere.com"
echo "Panel de administración: https://dalej.pythonanywhere.com/admin/"
echo

echo "=== FIN DEL DIAGNÓSTICO ==="
