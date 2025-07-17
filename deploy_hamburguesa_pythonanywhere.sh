#!/bin/bash

# COMANDOS PARA DESPLEGAR MENÚ HAMBURGUESA EN PYTHONANYWHERE
# Ejecutar estos comandos uno por uno en la consola bash de PythonAnywhere

echo "=== PASO 1: NAVEGAR AL DIRECTORIO DEL PROYECTO ==="
cd /home/dalej/multi

echo "=== PASO 2: VERIFICAR ESTADO ACTUAL ==="
git status

echo "=== PASO 3: DESCARGAR CAMBIOS DESDE GITHUB ==="
git pull origin main

echo "=== PASO 4: CONFIGURAR ALLOWED_HOSTS ==="
echo "Editando settings.py para agregar el dominio de PythonAnywhere..."
# Backup del archivo settings
cp multiandamios/settings.py multiandamios/settings.py.backup

# Agregar el dominio a ALLOWED_HOSTS
# Verificar si el archivo existe
if [ ! -f "multiandamios/settings.py" ]; then
    echo "Error: No se encontró el archivo multiandamios/settings.py"
    echo "Verificando estructura del proyecto..."
    ls -la
    exit 1
fi

# Verificar el contenido actual de ALLOWED_HOSTS
echo "Contenido actual de ALLOWED_HOSTS:"
grep -n "ALLOWED_HOSTS" multiandamios/settings.py

# Usar un patrón más flexible para el reemplazo
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py

# Verificar que el cambio se aplicó
echo "Nuevo contenido de ALLOWED_HOSTS:"
grep -n "ALLOWED_HOSTS" multiandamios/settings.py

echo "=== PASO 5: VERIFICAR QUE LOS CAMBIOS SE DESCARGARON ==="
git log --oneline -3

echo "=== PASO 6: VERIFICAR ARCHIVO BASE.HTML ==="
ls -la templates/base.html

echo "=== PASO 7: REINICIAR LA APLICACIÓN WEB ==="
touch /var/www/dalej_pythonanywhere_com_wsgi.py

echo "=== PASO 8: ACTUALIZAR ARCHIVOS ESTÁTICOS ==="
python manage.py collectstatic --noinput

echo "=== PASO 9: VERIFICAR QUE NO HAY ERRORES ==="
python manage.py check

echo "=== DESPLIEGUE COMPLETADO ==="
echo "Mejoras implementadas:"
echo "✅ Menú hamburguesa completamente funcional"
echo "✅ Formulario de agregar cliente REPARADO:"
echo "   - Transacciones atómicas para evitar inconsistencias"
echo "   - Manejo robusto de errores UNIQUE constraint"
echo "   - Validación mejorada en frontend y backend"
echo "   - Mejor feedback de errores al usuario"
echo "   - Limpieza automática de registros fallidos"
echo "   - Soporte completo para nuevos clientes"
echo "✅ Estilos CSS actualizados"
echo "✅ Scripts de diagnóstico y limpieza incluidos"
echo ""
echo "Sitio web: https://dalej.pythonanywhere.com/"
echo "Formulario de clientes: https://dalej.pythonanywhere.com/panel/admin/clientes/agregar/"
echo ""
echo "SCRIPTS DISPONIBLES:"
echo "- python limpiar_registros.py (limpia duplicados)"
echo "- python diagnostico_db.py (diagnóstico completo)"
echo "- python test_crear_cliente.py (test funcionalidad)"

# COMANDOS RESUMIDOS (ejecutar uno por uno):
# cd /home/dalej/multi
# git pull origin main
# ls -la multiandamios/settings.py  # Verificar que el archivo existe
# sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py
# touch /var/www/dalej_pythonanywhere_com_wsgi.py
# python manage.py collectstatic --noinput

# COMANDOS MANUALES SI EL SED NO FUNCIONA:
# nano multiandamios/settings.py
# Buscar la línea: ALLOWED_HOSTS = []
# Cambiar por: ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']
# Guardar con Ctrl+X, Y, Enter
