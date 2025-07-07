#!/usr/bin/env python
"""
Diagnóstico de permisos para recibos de obra
Verifica permisos de usuario y estado de pedidos para detectar problemas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.contrib.auth import get_user_model
from pedidos.models import Pedido
from usuarios.models import Cliente

User = get_user_model()

def diagnosticar_usuario(username=None):
    """Diagnostica los permisos de un usuario específico"""
    print("=" * 60)
    print("DIAGNÓSTICO DE PERMISOS PARA RECIBOS DE OBRA")
    print("=" * 60)
    
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"❌ Usuario '{username}' no encontrado")
            return
    else:
        # Mostrar usuarios admin/staff disponibles
        print("\n📋 USUARIOS ADMINISTRADORES DISPONIBLES:")
        admin_users = User.objects.filter(
            models.Q(is_staff=True) | 
            models.Q(rol__in=['admin', 'recibos_obra'])
        ).distinct()
        
        for user in admin_users:
            print(f"  • {user.username} - Staff: {user.is_staff}")
            if hasattr(user, 'rol'):
                print(f"    Rol: {user.rol}")
        
        if not admin_users.exists():
            print("  ❌ No se encontraron usuarios con permisos administrativos")
        
        return
    
    print(f"\n👤 USUARIO: {user.username}")
    print(f"   • Nombre completo: {user.get_full_name()}")
    print(f"   • Email: {user.email}")
    print(f"   • Is Staff: {user.is_staff}")
    print(f"   • Is Superuser: {user.is_superuser}")
    
    # Verificar si tiene perfil de cliente
    if hasattr(user, 'rol'):
        print(f"   • Rol de usuario: {user.rol}")
    
    # Verificar permisos para recibos
    puede_ver_recibos = user.is_staff or (hasattr(user, 'rol') and user.rol in ['admin', 'recibos_obra'])
    print(f"\n🔐 PERMISOS:")
    print(f"   • Puede ver recibos: {'✅ SÍ' if puede_ver_recibos else '❌ NO'}")
    
    if not puede_ver_recibos:
        print("\n💡 SOLUCIÓN:")
        print("   Para dar permisos de recibos de obra, debe:")
        print("   1. Marcar 'is_staff' = True en el usuario, O")
        print("   2. Asignar rol 'admin' o 'recibos_obra' en el usuario")
    
    return user

def diagnosticar_pedidos():
    """Diagnostica el estado de los pedidos para recibos de obra"""
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO DE PEDIDOS PARA RECIBOS DE OBRA")
    print("=" * 60)
    
    # Contar pedidos por estado
    estados_validos = ['entregado', 'recibido', 'pagado', 'en_preparacion', 'listo_entrega', 'programado_devolucion']
    
    print("\n📊 PEDIDOS POR ESTADO:")
    for estado in estados_validos:
        count = Pedido.objects.filter(estado_pedido_general=estado).count()
        print(f"   • {estado.replace('_', ' ').title()}: {count} pedidos")
    
    # Mostrar algunos pedidos de ejemplo
    print("\n📋 PEDIDOS DE EJEMPLO PARA CREAR RECIBOS:")
    pedidos_ejemplo = Pedido.objects.filter(
        estado_pedido_general__in=estados_validos
    ).order_by('-fecha')[:5]
    
    for pedido in pedidos_ejemplo:
        print(f"   • Pedido #{pedido.id_pedido}")
        print(f"     Cliente: {pedido.cliente}")
        print(f"     Estado: {pedido.get_estado_pedido_general_display()}")
        print(f"     Fecha: {pedido.fecha}")
        print(f"     Total: ${pedido.total}")
        
        # URL para crear recibo
        url = f"/recibos/crear-multiple/{pedido.id_pedido}/"
        print(f"     URL recibo: {url}")
        print()

def main():
    print("Ejecutando diagnóstico de permisos para recibos de obra...")
    
    # Primero mostrar usuarios disponibles
    diagnosticar_usuario()
    
    # Luego mostrar estado de pedidos
    diagnosticar_pedidos()
    
    print("\n" + "=" * 60)
    print("Para diagnosticar un usuario específico, ejecute:")
    print("python diagnostico_permisos_recibo.py <username>")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    from django.db import models
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        diagnosticar_usuario(username)
        diagnosticar_pedidos()
    else:
        main()
