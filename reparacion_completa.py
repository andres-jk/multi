#!/usr/bin/env python3
"""
Script de reparación completa para resolver el problema de clientes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection, transaction
from usuarios.models import Usuario, Cliente

print("=== REPARACIÓN COMPLETA DE CLIENTES ===")

# 1. Limpiar registros problemáticos
print("\n1. Limpiando registros problemáticos...")
with connection.cursor() as cursor:
    # Eliminar clientes con usuario_id NULL
    cursor.execute("DELETE FROM usuarios_cliente WHERE usuario_id IS NULL")
    deleted_null = cursor.rowcount
    print(f"   Eliminados {deleted_null} clientes con usuario_id NULL")
    
    # Eliminar duplicados manteniendo solo el más reciente
    cursor.execute("""
        DELETE FROM usuarios_cliente 
        WHERE id NOT IN (
            SELECT MAX(id) 
            FROM usuarios_cliente 
            GROUP BY usuario_id
        )
    """)
    deleted_dups = cursor.rowcount
    print(f"   Eliminados {deleted_dups} clientes duplicados")

# 2. Verificar estado actual
print("\n2. Verificando estado actual...")
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM usuarios_usuario")
    total_usuarios = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM usuarios_cliente")
    total_clientes = cursor.fetchone()[0]
    
    print(f"   Total usuarios: {total_usuarios}")
    print(f"   Total clientes: {total_clientes}")
    
    # Verificar problemas restantes
    cursor.execute("SELECT COUNT(*) FROM usuarios_cliente WHERE usuario_id IS NULL")
    nulos = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT usuario_id, COUNT(*) as count
            FROM usuarios_cliente 
            GROUP BY usuario_id 
            HAVING COUNT(*) > 1
        )
    """)
    duplicados = cursor.fetchone()[0]
    
    if nulos == 0 and duplicados == 0:
        print("   ✅ Base de datos limpia")
    else:
        print(f"   ❌ Problemas restantes: {nulos} nulos, {duplicados} duplicados")

# 3. Probar creación de cliente
print("\n3. Probando creación de cliente...")
try:
    with transaction.atomic():
        import uuid
        username = f"test_repair_{uuid.uuid4().hex[:6]}"
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=username,
            password="test123456",
            email=f"{username}@test.com",
            first_name="Test",
            last_name="Repair"
        )
        usuario.rol = 'cliente'
        usuario.numero_identidad = f"ID{uuid.uuid4().hex[:8]}"
        usuario.save()
        
        # Crear cliente
        cliente = Cliente.objects.create(
            usuario=usuario,
            telefono="3001234567",
            direccion="Test Repair Address"
        )
        
        print(f"   ✅ Cliente creado exitosamente:")
        print(f"      Usuario: {usuario.username} (ID: {usuario.id})")
        print(f"      Cliente: {cliente.id}")
        print(f"      Email: {usuario.email}")
        
        success = True
        
except Exception as e:
    print(f"   ❌ Error al crear cliente: {e}")
    success = False

# 4. Resultado final
print("\n4. Resultado final:")
if success:
    print("   🎉 SISTEMA REPARADO EXITOSAMENTE")
    print("   Los clientes ahora se pueden crear sin problemas")
else:
    print("   ❌ El problema persiste - se requiere intervención manual")

print("\n=== REPARACIÓN COMPLETADA ===")
