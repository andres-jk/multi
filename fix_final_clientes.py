#!/usr/bin/env python3
"""
Script final para resolver el problema de creación de clientes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection, transaction
from usuarios.models import Usuario, Cliente

def resolver_problema_clientes():
    """Resuelve el problema de creación de clientes de forma definitiva"""
    print("=== RESOLUCIÓN DEFINITIVA DEL PROBLEMA DE CLIENTES ===")
    
    with connection.cursor() as cursor:
        # 1. Verificar el problema actual
        print("1. Verificando problema actual...")
        cursor.execute("SELECT COUNT(*) FROM usuarios_cliente WHERE usuario_id IS NULL")
        nulos = cursor.fetchone()[0]
        print(f"   Clientes con usuario_id NULL: {nulos}")
        
        cursor.execute("""
            SELECT usuario_id, COUNT(*) as count
            FROM usuarios_cliente 
            GROUP BY usuario_id 
            HAVING COUNT(*) > 1
        """)
        duplicados = cursor.fetchall()
        print(f"   Usuarios con múltiples clientes: {len(duplicados)}")
        
        # 2. Eliminar registros problemáticos
        print("\n2. Eliminando registros problemáticos...")
        
        # Eliminar clientes con usuario_id NULL
        cursor.execute("DELETE FROM usuarios_cliente WHERE usuario_id IS NULL")
        deleted_null = cursor.rowcount
        print(f"   Eliminados {deleted_null} clientes con usuario_id NULL")
        
        # Eliminar duplicados, manteniendo solo el más reciente
        for usuario_id, count in duplicados:
            cursor.execute("""
                DELETE FROM usuarios_cliente 
                WHERE usuario_id = ? AND id NOT IN (
                    SELECT id FROM usuarios_cliente 
                    WHERE usuario_id = ? 
                    ORDER BY id DESC 
                    LIMIT 1
                )
            """, [usuario_id, usuario_id])
            deleted_dups = cursor.rowcount
            print(f"   Eliminados {deleted_dups} duplicados para usuario {usuario_id}")
        
        # 3. Recrear el índice único si es necesario
        print("\n3. Verificando índice único...")
        try:
            cursor.execute("DROP INDEX IF EXISTS usuarios_cliente_usuario_id_unique")
            cursor.execute("CREATE UNIQUE INDEX usuarios_cliente_usuario_id_unique ON usuarios_cliente(usuario_id)")
            print("   ✓ Índice único recreado")
        except Exception as e:
            print(f"   ⚠️  Error al recrear índice: {e}")
        
        # 4. Verificar estado final
        print("\n4. Verificando estado final...")
        cursor.execute("SELECT COUNT(*) FROM usuarios_cliente")
        total_clientes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios_usuario")
        total_usuarios = cursor.fetchone()[0]
        
        print(f"   Total usuarios: {total_usuarios}")
        print(f"   Total clientes: {total_clientes}")
        
        # Verificar que no haya más problemas
        cursor.execute("SELECT COUNT(*) FROM usuarios_cliente WHERE usuario_id IS NULL")
        nulos_final = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT usuario_id, COUNT(*) as count
                FROM usuarios_cliente 
                GROUP BY usuario_id 
                HAVING COUNT(*) > 1
            )
        """)
        duplicados_final = cursor.fetchone()[0]
        
        if nulos_final == 0 and duplicados_final == 0:
            print("   ✅ Base de datos limpia - No hay problemas")
        else:
            print(f"   ❌ Aún hay problemas: {nulos_final} nulos, {duplicados_final} duplicados")
        
        return nulos_final == 0 and duplicados_final == 0

def probar_creacion_cliente():
    """Prueba la creación de un cliente"""
    print("\n=== PRUEBA DE CREACIÓN DE CLIENTE ===")
    
    try:
        with transaction.atomic():
            import uuid
            username = f"test_final_{uuid.uuid4().hex[:6]}"
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                username=username,
                password="test123456",
                email=f"{username}@test.com",
                first_name="Test",
                last_name="Final"
            )
            usuario.rol = 'cliente'
            usuario.numero_identidad = f"ID{uuid.uuid4().hex[:8]}"
            usuario.save()
            
            # Crear cliente
            cliente = Cliente.objects.create(
                usuario=usuario,
                telefono="3001234567",
                direccion="Test Final Address"
            )
            
            print(f"✅ Cliente creado exitosamente:")
            print(f"   Usuario: {usuario.username} (ID: {usuario.id})")
            print(f"   Cliente: {cliente.id}")
            print(f"   Email: {usuario.email}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error al crear cliente: {e}")
        return False

def main():
    if resolver_problema_clientes():
        print("\n✅ Problema resuelto en base de datos")
        
        if probar_creacion_cliente():
            print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
            print("   Los clientes ahora se pueden crear sin problemas")
        else:
            print("\n❌ El problema persiste después de la reparación")
    else:
        print("\n❌ No se pudo resolver el problema en la base de datos")
    
    print("\n=== PROCESO COMPLETADO ===")

if __name__ == "__main__":
    main()
