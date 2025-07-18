#!/usr/bin/env python
"""
Script simple para limpiar la base de datos de clientes problemáticos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import Usuario, Cliente
from django.db import transaction

def limpiar_bd():
    print("Iniciando limpieza de base de datos...")
    
    try:
        with transaction.atomic():
            # 1. Eliminar todos los clientes huérfanos (sin usuario)
            clientes_huerfanos = Cliente.objects.filter(usuario__isnull=True)
            count_huerfanos = clientes_huerfanos.count()
            clientes_huerfanos.delete()
            print(f"Eliminados {count_huerfanos} clientes huérfanos")
            
            # 2. Para cada usuario, asegurar que solo tenga un cliente
            for usuario in Usuario.objects.all():
                clientes = Cliente.objects.filter(usuario=usuario)
                if clientes.count() > 1:
                    # Mantener el primer cliente, eliminar el resto
                    cliente_a_mantener = clientes.first()
                    clientes_a_eliminar = clientes.exclude(id=cliente_a_mantener.id)
                    count_eliminados = clientes_a_eliminar.count()
                    clientes_a_eliminar.delete()
                    print(f"Usuario {usuario.username}: eliminados {count_eliminados} clientes duplicados")
            
            # 3. Crear clientes para usuarios de rol 'cliente' que no tienen cliente
            usuarios_sin_cliente = Usuario.objects.filter(rol='cliente', cliente__isnull=True)
            for usuario in usuarios_sin_cliente:
                Cliente.objects.create(
                    usuario=usuario,
                    telefono='',
                    direccion=''
                )
                print(f"Cliente creado para usuario: {usuario.username}")
            
            print("Limpieza completada exitosamente")
            
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    limpiar_bd()
