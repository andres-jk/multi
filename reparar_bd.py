#!/usr/bin/env python3
"""
Script para reparar la base de datos manualmente
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection, transaction
from usuarios.models import Usuario, Cliente

def reparar_base_de_datos():
    """Repara la base de datos eliminando registros problemáticos"""
    print("=== REPARACIÓN DE BASE DE DATOS ===")
    
    with connection.cursor() as cursor:
        # 1. Eliminar todos los clientes con usuario_id NULL
        print("1. Eliminando clientes con usuario_id NULL...")
        cursor.execute("DELETE FROM usuarios_cliente WHERE usuario_id IS NULL")
        deleted_null = cursor.rowcount
        print(f"   Eliminados {deleted_null} clientes con usuario_id NULL")
        
        # 2. Eliminar clientes duplicados (mantener solo el más reciente)
        print("2. Eliminando clientes duplicados...")
        cursor.execute("""
            DELETE FROM usuarios_cliente 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM usuarios_cliente 
                GROUP BY usuario_id
            )
        """)
        deleted_duplicates = cursor.rowcount
        print(f"   Eliminados {deleted_duplicates} clientes duplicados")
        
        # 3. Verificar que no haya clientes huérfanos
        print("3. Eliminando clientes huérfanos...")
        cursor.execute("""
            DELETE FROM usuarios_cliente 
            WHERE usuario_id NOT IN (SELECT id FROM usuarios_usuario)
        """)
        deleted_orphans = cursor.rowcount
        print(f"   Eliminados {deleted_orphans} clientes huérfanos")
        
        # 4. Verificar el estado final
        print("4. Verificando estado final...")
        cursor.execute("SELECT COUNT(*) FROM usuarios_cliente")
        total_clientes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios_usuario")
        total_usuarios = cursor.fetchone()[0]
        
        print(f"   Total usuarios: {total_usuarios}")
        print(f"   Total clientes: {total_clientes}")
        
        # 5. Verificar que no haya duplicados
        cursor.execute("""
            SELECT usuario_id, COUNT(*) as count
            FROM usuarios_cliente 
            GROUP BY usuario_id 
            HAVING COUNT(*) > 1
        """)
        duplicados = cursor.fetchall()
        
        if duplicados:
            print(f"   ⚠️  Aún hay {len(duplicados)} duplicados")
            for dup in duplicados:
                print(f"      Usuario ID {dup[0]}: {dup[1]} clientes")
        else:
            print("   ✓ No hay duplicados")
        
        # 6. Intentar recrear el constraint si es necesario
        print("5. Verificando constraint único...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='usuarios_cliente' 
            AND sql LIKE '%UNIQUE%usuario_id%'
        """)
        unique_constraint = cursor.fetchone()
        
        if unique_constraint:
            print(f"   ✓ Constraint único existe: {unique_constraint[0]}")
        else:
            print("   ⚠️  Constraint único no encontrado")
            
            # Crear constraint único si no existe
            try:
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS usuarios_cliente_usuario_id_unique 
                    ON usuarios_cliente(usuario_id)
                """)
                print("   ✓ Constraint único creado")
            except Exception as e:
                print(f"   ✗ Error al crear constraint: {e}")

def probar_creacion_cliente():
    """Prueba la creación de un cliente"""
    print("\n=== PRUEBA DE CREACIÓN DE CLIENTE ===")
    
    try:
        with transaction.atomic():
            import uuid
            username = f"test_repair_{uuid.uuid4().hex[:8]}"
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                username=username,
                password="testpass123",
                email=f"{username}@test.com",
                first_name="Test",
                last_name="Repair"
            )
            usuario.rol = 'cliente'
            usuario.save()
            
            # Crear cliente
            cliente = Cliente.objects.create(
                usuario=usuario,
                telefono="123456789",
                direccion="Test Address"
            )
            
            print(f"✓ Cliente creado exitosamente: {username}")
            print(f"  Usuario ID: {usuario.id}")
            print(f"  Cliente ID: {cliente.id}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error al crear cliente: {e}")
        return False

def main():
    reparar_base_de_datos()
    probar_creacion_cliente()
    print("\n=== REPARACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()
