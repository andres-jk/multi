#!/usr/bin/env python
"""
Script para diagnosticar el problema con la creación de clientes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import Usuario, Cliente

def diagnosticar_clientes():
    print("=== DIAGNÓSTICO DE CLIENTES ===")
    
    # 1. Verificar usuarios huérfanos (sin cliente)
    usuarios_sin_cliente = Usuario.objects.filter(cliente__isnull=True)
    print(f"\n1. Usuarios sin cliente: {usuarios_sin_cliente.count()}")
    for usuario in usuarios_sin_cliente:
        print(f"   - {usuario.username} ({usuario.rol}) ID: {usuario.id}")
    
    # 2. Verificar clientes huérfanos (sin usuario)
    clientes_sin_usuario = Cliente.objects.filter(usuario__isnull=True)
    print(f"\n2. Clientes sin usuario: {clientes_sin_usuario.count()}")
    for cliente in clientes_sin_usuario:
        print(f"   - Cliente ID: {cliente.id}")
    
    # 3. Verificar usuarios con cliente
    usuarios_con_cliente = Usuario.objects.filter(cliente__isnull=False)
    print(f"\n3. Usuarios con cliente: {usuarios_con_cliente.count()}")
    
    # 4. Verificar duplicados de cliente
    print(f"\n4. Verificando duplicados...")
    duplicados = []
    for usuario in Usuario.objects.all():
        clientes_count = Cliente.objects.filter(usuario=usuario).count()
        if clientes_count > 1:
            duplicados.append((usuario.username, clientes_count))
    
    if duplicados:
        print(f"   Usuarios con múltiples clientes: {len(duplicados)}")
        for username, count in duplicados:
            print(f"   - {username}: {count} clientes")
    else:
        print("   No hay duplicados")
    
    # 5. Verificar la tabla Cliente directamente
    print(f"\n5. Total de registros en tabla Cliente: {Cliente.objects.count()}")
    print(f"   Total de registros en tabla Usuario: {Usuario.objects.count()}")
    
    # 6. Verificar el signal
    print(f"\n6. Verificando signal...")
    try:
        from django.db.models.signals import post_save
        from usuarios.signals import create_cliente_profile
        
        # Verificar si el signal está conectado
        connections = post_save._live_receivers(sender=Usuario)
        signal_connected = any(receiver.__name__ == 'create_cliente_profile' for receiver in connections)
        print(f"   Signal conectado: {signal_connected}")
    except Exception as e:
        print(f"   Error al verificar signal: {e}")
    
    # 7. Intentar crear un usuario de prueba
    print(f"\n7. Probando creación de usuario de prueba...")
    try:
        # Verificar si ya existe
        if Usuario.objects.filter(username='test_cliente_temp').exists():
            print("   Usuario de prueba ya existe, eliminándolo...")
            Usuario.objects.filter(username='test_cliente_temp').delete()
        
        # Crear usuario
        usuario_prueba = Usuario.objects.create_user(
            username='test_cliente_temp',
            password='test123',
            rol='cliente'
        )
        print(f"   Usuario creado: {usuario_prueba.username}")
        
        # Verificar si se creó el cliente
        if hasattr(usuario_prueba, 'cliente'):
            print(f"   Cliente creado automáticamente: SÍ")
            print(f"   Cliente ID: {usuario_prueba.cliente.id}")
        else:
            print(f"   Cliente creado automáticamente: NO")
        
        # Limpiar
        usuario_prueba.delete()
        print("   Usuario de prueba eliminado")
        
    except Exception as e:
        print(f"   Error en prueba: {e}")
    
    print("\n=== FIN DIAGNÓSTICO ===")

if __name__ == '__main__':
    diagnosticar_clientes()
