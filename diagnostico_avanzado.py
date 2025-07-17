#!/usr/bin/env python3
"""
Diagnóstico avanzado de la base de datos para problemas de creación de clientes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario, Cliente

def main():
    print("=== DIAGNÓSTICO AVANZADO DE BASE DE DATOS ===")
    
    # 1. Verificar usuarios sin clientes
    print("\n1. Usuarios sin clientes asociados:")
    usuarios_sin_clientes = Usuario.objects.filter(cliente__isnull=True)
    for usuario in usuarios_sin_clientes:
        print(f"   - {usuario.username} ({usuario.email}) - ID: {usuario.id}")
    
    # 2. Verificar clientes sin usuarios
    print("\n2. Clientes huérfanos (sin usuario):")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, usuario_id, telefono, direccion 
            FROM usuarios_cliente 
            WHERE usuario_id NOT IN (SELECT id FROM usuarios_usuario)
        """)
        clientes_huerfanos = cursor.fetchall()
        for cliente in clientes_huerfanos:
            print(f"   - Cliente ID: {cliente[0]}, Usuario ID inexistente: {cliente[1]}")
    
    # 3. Verificar duplicados en cliente por usuario_id
    print("\n3. Duplicados en usuarios_cliente por usuario_id:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT usuario_id, COUNT(*) as count
            FROM usuarios_cliente 
            GROUP BY usuario_id 
            HAVING COUNT(*) > 1
        """)
        duplicados = cursor.fetchall()
        for dup in duplicados:
            print(f"   - Usuario ID {dup[0]}: {dup[1]} clientes")
            
            # Mostrar detalles de los duplicados
            cursor.execute("""
                SELECT id, telefono, direccion, created_at
                FROM usuarios_cliente 
                WHERE usuario_id = ?
                ORDER BY created_at DESC
            """, [dup[0]])
            detalles = cursor.fetchall()
            for detalle in detalles:
                print(f"     * Cliente ID: {detalle[0]}, Tel: {detalle[1]}, Dir: {detalle[2]}, Fecha: {detalle[3]}")
    
    # 4. Verificar constraints en la tabla
    print("\n4. Información de constraints:")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(usuarios_cliente)")
        info = cursor.fetchall()
        for campo in info:
            print(f"   - {campo[1]} ({campo[2]}) - Not Null: {campo[3]}, Default: {campo[4]}, PK: {campo[5]}")
    
    # 5. Verificar índices únicos
    print("\n5. Índices únicos:")
    with connection.cursor() as cursor:
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='usuarios_cliente'")
        indices = cursor.fetchall()
        for indice in indices:
            print(f"   - {indice[0]}: {indice[1]}")
    
    # 6. Contar registros totales
    print("\n6. Resumen de registros:")
    total_usuarios = Usuario.objects.count()
    total_clientes = Cliente.objects.count()
    print(f"   - Total usuarios: {total_usuarios}")
    print(f"   - Total clientes: {total_clientes}")
    
    # 7. Verificar últimos registros
    print("\n7. Últimos 5 usuarios creados:")
    ultimos_usuarios = Usuario.objects.order_by('-id')[:5]
    for usuario in ultimos_usuarios:
        tiene_cliente = hasattr(usuario, 'cliente') and usuario.cliente is not None
        print(f"   - {usuario.username} (ID: {usuario.id}) - Tiene cliente: {tiene_cliente}")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    main()
