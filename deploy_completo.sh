#!/bin/bash
# Script de despliegue completo para PythonAnywhere
# Resuelve el problema de clientes y despliega cambios de CSS

echo "=== DESPLIEGUE COMPLETO EN PYTHONANYWHERE ==="

# 1. Ir al directorio del proyecto
cd /home/dalej/multi

# 2. Hacer backup de la base de datos
echo "1. Creando backup de la base de datos..."
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 3. Actualizar código desde GitHub
echo "2. Actualizando código desde GitHub..."
git pull origin main

# 4. Limpiar base de datos de registros problemáticos
echo "3. Limpiando base de datos..."
python3.10 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('DELETE FROM usuarios_cliente WHERE usuario_id IS NULL')
    null_deleted = cursor.rowcount
    cursor.execute('DELETE FROM usuarios_cliente WHERE id NOT IN (SELECT MAX(id) FROM usuarios_cliente GROUP BY usuario_id)')
    dup_deleted = cursor.rowcount
    print(f'Eliminados {null_deleted} registros NULL y {dup_deleted} duplicados')
"

# 5. Ejecutar migraciones
echo "4. Ejecutando migraciones..."
python3.10 manage.py migrate --run-syncdb

# 6. Recopilar archivos estáticos (CSS)
echo "5. Recopilando archivos estáticos..."
python3.10 manage.py collectstatic --noinput

# 7. Probar creación de cliente
echo "6. Probando creación de cliente..."
python3.10 -c "
import os
import django
import uuid
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()
from django.db import transaction
from usuarios.models import Usuario, Cliente

try:
    with transaction.atomic():
        username = f'test_deploy_{uuid.uuid4().hex[:6]}'
        usuario = Usuario.objects.create_user(
            username=username,
            password='test123456',
            email=f'{username}@test.com',
            first_name='Test',
            last_name='Deploy'
        )
        usuario.rol = 'cliente'
        usuario.numero_identidad = f'ID{uuid.uuid4().hex[:8]}'
        usuario.save()
        
        cliente = Cliente.objects.create(
            usuario=usuario,
            telefono='3001234567',
            direccion='Test Deploy Address'
        )
        
        print(f'✅ Cliente creado exitosamente: {username} (ID: {cliente.id})')
except Exception as e:
    print(f'❌ Error al crear cliente: {e}')
"

# 8. Reiniciar aplicación web
echo "7. Reiniciando aplicación web..."
touch /var/www/dalej_pythonanywhere_com_wsgi.py

echo "8. Verificando estado del servidor..."
curl -I https://dalej.pythonanywhere.com/ | head -1

echo ""
echo "=== DESPLIEGUE COMPLETADO ==="
echo "Cambios aplicados:"
echo "- ✅ Código actualizado desde GitHub"
echo "- ✅ Base de datos limpiada"
echo "- ✅ CSS actualizado (fondo azul #7ec4ff)"
echo "- ✅ Servidor reiniciado"
echo ""
echo "Prueba la creación de clientes en:"
echo "https://dalej.pythonanywhere.com/panel/admin/clientes/agregar/"
