#!/usr/bin/env python3
"""
Script simple para limpiar la base de datos antes de crear clientes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection, transaction
from usuarios.models import Usuario, Cliente

def limpiar_base_datos():
    """Limpia la base de datos de registros problemáticos"""
    print("Limpiando base de datos...")
    
    with connection.cursor() as cursor:
        # Eliminar clientes con usuario_id NULL
        cursor.execute("DELETE FROM usuarios_cliente WHERE usuario_id IS NULL")
        deleted_null = cursor.rowcount
        
        # Eliminar duplicados
        cursor.execute("""
            DELETE FROM usuarios_cliente 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM usuarios_cliente 
                GROUP BY usuario_id
            )
        """)
        deleted_dups = cursor.rowcount
        
        print(f"Eliminados {deleted_null} registros con usuario_id NULL")
        print(f"Eliminados {deleted_dups} registros duplicados")
        
        # Contar registros finales
        cursor.execute("SELECT COUNT(*) FROM usuarios_cliente")
        total = cursor.fetchone()[0]
        print(f"Total clientes restantes: {total}")

def crear_cliente_prueba():
    """Crear un cliente de prueba"""
    print("\nCreando cliente de prueba...")
    
    try:
        import uuid
        username = f"test_{uuid.uuid4().hex[:6]}"
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=username,
            password="test123",
            email=f"{username}@test.com",
            first_name="Test",
            last_name="User"
        )
        usuario.rol = 'cliente'
        usuario.save()
        
        # Crear cliente
        cliente = Cliente.objects.create(
            usuario=usuario,
            telefono="123456789",
            direccion="Test Address"
        )
        
        print(f"✓ Cliente creado: {username} (ID: {cliente.id})")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# Ejecutar limpieza y prueba
limpiar_base_datos()
if crear_cliente_prueba():
    print("\n✅ SISTEMA FUNCIONAL - Los clientes se pueden crear correctamente")
else:
    print("\n❌ El problema persiste")
