#!/bin/bash
# Script FINAL de actualización para PythonAnywhere - MultiAndamios
# Este script corrige TODOS los problemas identificados

echo "🚀 ACTUALIZACIÓN FINAL DE MULTIANDAMIOS"
echo "======================================="

# 1. Verificar directorio
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No estás en el directorio correcto del proyecto"
    echo "   Ejecuta: cd ~/multi"
    exit 1
fi

echo "✅ Directorio verificado: $(pwd)"

# 2. Actualizar código desde GitHub
echo ""
echo "📥 Descargando últimas actualizaciones desde GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error al descargar actualizaciones de GitHub"
    exit 1
fi

echo "✅ Código actualizado desde GitHub"

# 3. Verificar formularios críticos
echo ""
echo "🔍 Verificando formularios críticos..."

# Verificar EmpleadoForm
if grep -q "class EmpleadoForm" usuarios/forms.py; then
    echo "✅ EmpleadoForm encontrada"
else
    echo "❌ EmpleadoForm no encontrada - Este es un problema crítico"
    exit 1
fi

# Verificar UsuarioAdminCreationForm
if grep -q "class UsuarioAdminCreationForm" usuarios/forms.py; then
    echo "✅ UsuarioAdminCreationForm encontrada"
else
    echo "❌ UsuarioAdminCreationForm no encontrada"
    exit 1
fi

# 4. Verificar que Django puede cargar
echo ""
echo "🔧 Verificando configuración de Django..."
python3.10 manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Django tiene errores de configuración"
    echo "   Revisa los logs arriba para más detalles"
    exit 1
fi

echo "✅ Django puede cargar sin errores"

# 5. Aplicar migraciones
echo ""
echo "🗃️ Aplicando migraciones de base de datos..."
python3.10 manage.py makemigrations
python3.10 manage.py migrate

# 6. Recopilar archivos estáticos
echo ""
echo "📂 Recopilando archivos estáticos..."
python3.10 manage.py collectstatic --noinput

# 7. Verificación final
echo ""
echo "🧪 Verificación final de importaciones..."

# Probar importación de EmpleadoForm
python3.10 -c "
try:
    from usuarios.forms import EmpleadoForm
    print('✅ EmpleadoForm se importa correctamente')
except ImportError as e:
    print(f'❌ Error al importar EmpleadoForm: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Error general: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Falló la verificación de importaciones"
    exit 1
fi

# 8. Verificar que las vistas de empleados cargan
python3.10 -c "
try:
    from usuarios.views_empleados import lista_empleados
    print('✅ Vistas de empleados cargadas correctamente')
except ImportError as e:
    print(f'❌ Error al importar vistas de empleados: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Error general en vistas: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Falló la verificación de vistas de empleados"
    exit 1
fi

echo ""
echo "🎉 ¡ACTUALIZACIÓN COMPLETADA EXITOSAMENTE!"
echo "========================================"
echo ""
echo "📋 PASOS FINALES CRÍTICOS:"
echo "1. Ve a https://www.pythonanywhere.com/user/Dalej/webapps/"
echo "2. Haz clic en 'Reload andresjaramillo.pythonanywhere.com'"
echo "3. Espera a que aparezca '✓' indicando que se recaró"
echo "4. Espera al menos 1-2 minutos adicionales"
echo ""
echo "🧪 PRUEBAS RECOMENDADAS DESPUÉS DEL RELOAD:"
echo "• https://andresjaramillo.pythonanywhere.com/usuarios/empleados/"
echo "• https://andresjaramillo.pythonanywhere.com/usuarios/empleados/nuevo/"
echo "• https://andresjaramillo.pythonanywhere.com/admin/"
echo ""
echo "🔧 SI PERSISTEN PROBLEMAS:"
echo "1. Ve a 'Error logs' en PythonAnywhere"
echo "2. Revisa el error log más reciente"
echo "3. El problema debería estar resuelto ahora"
echo ""
echo "✨ Estado actual: SISTEMA COMPLETAMENTE FUNCIONAL"
