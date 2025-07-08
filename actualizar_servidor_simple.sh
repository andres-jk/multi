#!/bin/bash
# Script de actualización SIMPLIFICADO para PythonAnywhere

echo "🚀 ACTUALIZACIÓN SIMPLIFICADA DE MULTIANDAMIOS"
echo "=============================================="

# 1. Verificar directorio
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No estás en el directorio correcto"
    echo "   Ejecuta: cd ~/multi"
    exit 1
fi

echo "✅ Directorio verificado: $(pwd)"

# 2. Actualizar código
echo ""
echo "📥 Actualizando desde GitHub..."
git pull origin main
echo "✅ Código actualizado"

# 3. Verificar Django
echo ""
echo "🔧 Verificando Django..."
python3.10 manage.py check
if [ $? -eq 0 ]; then
    echo "✅ Django funciona correctamente"
else
    echo "❌ Django tiene errores"
    exit 1
fi

# 4. Migraciones
echo ""
echo "🗃️ Aplicando migraciones..."
python3.10 manage.py makemigrations
python3.10 manage.py migrate

# 5. Archivos estáticos
echo ""
echo "📂 Recopilando archivos estáticos..."
python3.10 manage.py collectstatic --noinput

# 6. Verificación con Django configurado
echo ""
echo "🧪 Verificando importaciones críticas..."
python3.10 verificar_importaciones.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ¡ACTUALIZACIÓN EXITOSA!"
    echo "========================"
    echo ""
    echo "✅ Todas las verificaciones pasaron"
    echo "✅ El sistema está listo para funcionar"
    echo ""
    echo "📋 PRÓXIMO PASO CRÍTICO:"
    echo "1. Ve a: https://www.pythonanywhere.com/user/Dalej/webapps/"
    echo "2. Haz clic en 'Reload andresjaramillo.pythonanywhere.com'"
    echo "3. Espera a que aparezca ✓"
    echo ""
    echo "🧪 DESPUÉS DEL RELOAD, PRUEBA:"
    echo "• https://andresjaramillo.pythonanywhere.com/usuarios/empleados/"
    echo "• https://andresjaramillo.pythonanywhere.com/usuarios/empleados/nuevo/"
    echo ""
    echo "✨ El problema del ImportError debería estar RESUELTO"
else
    echo ""
    echo "❌ Falló la verificación de importaciones"
    echo "   Revisa los errores arriba"
    exit 1
fi
