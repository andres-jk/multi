#!/usr/bin/env python3
"""
Script para resetear completamente la tabla de clientes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection, transaction
from usuarios.models import Usuario, Cliente

def resetear_tabla_clientes():
    """Resetea completamente la tabla de clientes"""
    print("=== RESETEO COMPLETO DE TABLA CLIENTES ===")
    
    with connection.cursor() as cursor:
        # 1. Eliminar toda la tabla de clientes
        print("1. Eliminando todos los registros de clientes...")
        cursor.execute("DELETE FROM usuarios_cliente")
        deleted = cursor.rowcount
        print(f"   Eliminados {deleted} registros")
        
        # 2. Resetear el contador de auto-increment
        print("2. Reseteando contador de ID...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='usuarios_cliente'")
        
        # 3. Verificar que la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM usuarios_cliente")
        count = cursor.fetchone()[0]
        print(f"   Registros restantes: {count}")
        
        # 4. Verificar la estructura de la tabla
        print("3. Verificando estructura de la tabla...")
        cursor.execute("PRAGMA table_info(usuarios_cliente)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - Not Null: {col[3]}, Default: {col[4]}, PK: {col[5]}")
        
        # 5. Verificar índices únicos
        print("4. Verificando índices únicos...")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='usuarios_cliente'")
        indices = cursor.fetchall()
        for idx in indices:
            print(f"   {idx[0]}: {idx[1]}")

def crear_cliente_limpio():
    """Crea un cliente desde cero en tabla limpia"""
    print("\n=== CREACIÓN DE CLIENTE EN TABLA LIMPIA ===")
    
    try:
        with transaction.atomic():
            # Crear usuario único
            import uuid
            username = f"clean_user_{uuid.uuid4().hex[:8]}"
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                username=username,
                password="test123456",
                email=f"{username}@test.com",
                first_name="Test",
                last_name="Clean"
            )
            usuario.rol = 'cliente'
            usuario.numero_identidad = f"ID{uuid.uuid4().hex[:10]}"
            usuario.save()
            
            print(f"✓ Usuario creado: {usuario.username} (ID: {usuario.id})")
            
            # Crear cliente
            cliente = Cliente.objects.create(
                usuario=usuario,
                telefono="3001234567",
                direccion="Test Address Clean"
            )
            
            print(f"✓ Cliente creado exitosamente:")
            print(f"  Cliente ID: {cliente.id}")
            print(f"  Usuario ID: {cliente.usuario.id}")
            print(f"  Teléfono: {cliente.telefono}")
            print(f"  Dirección: {cliente.direccion}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error al crear cliente: {e}")
        return False

def verificar_funcionamiento():
    """Verifica que el sistema funciona correctamente después del reset"""
    print("\n=== VERIFICACIÓN FINAL ===")
    
    try:
        # Contar registros
        total_usuarios = Usuario.objects.count()
        total_clientes = Cliente.objects.count()
        
        print(f"📊 Total usuarios: {total_usuarios}")
        print(f"📊 Total clientes: {total_clientes}")
        
        # Verificar relaciones
        usuarios_con_cliente = Usuario.objects.filter(cliente__isnull=False).count()
        print(f"📊 Usuarios con cliente: {usuarios_con_cliente}")
        
        # Intentar crear otro cliente
        print("\n5. Intentando crear segundo cliente...")
        import uuid
        username2 = f"clean_user2_{uuid.uuid4().hex[:8]}"
        
        usuario2 = Usuario.objects.create_user(
            username=username2,
            password="test123456",
            email=f"{username2}@test.com",
            first_name="Test2",
            last_name="Clean2"
        )
        usuario2.rol = 'cliente'
        usuario2.numero_identidad = f"ID{uuid.uuid4().hex[:10]}"
        usuario2.save()
        
        cliente2 = Cliente.objects.create(
            usuario=usuario2,
            telefono="3007654321",
            direccion="Test Address Clean 2"
        )
        
        print(f"✓ Segundo cliente creado exitosamente: {cliente2.id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en verificación: {e}")
        return False

def main():
    resetear_tabla_clientes()
    
    if crear_cliente_limpio():
        if verificar_funcionamiento():
            print("\n✅ SISTEMA REPARADO EXITOSAMENTE")
            print("   El sistema de creación de clientes funciona correctamente")
        else:
            print("\n❌ SISTEMA AÚN TIENE PROBLEMAS")
    else:
        print("\n❌ FALLO EN LA REPARACIÓN")
    
    print("\n=== PROCESO COMPLETADO ===")

if __name__ == "__main__":
    main()
