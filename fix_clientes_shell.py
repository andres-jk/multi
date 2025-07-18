"""
Script para ejecutar dentro del shell de Django
python manage.py shell < fix_clientes_shell.py
"""

from usuarios.models import Usuario, Cliente
from django.db import transaction

print("=== LIMPIEZA DE CLIENTES ===")

with transaction.atomic():
    # 1. Eliminar clientes huérfanos
    clientes_huerfanos = Cliente.objects.filter(usuario__isnull=True)
    count_huerfanos = clientes_huerfanos.count()
    clientes_huerfanos.delete()
    print(f"Eliminados {count_huerfanos} clientes huérfanos")
    
    # 2. Eliminar duplicados
    duplicados_eliminados = 0
    for usuario in Usuario.objects.all():
        clientes = Cliente.objects.filter(usuario=usuario)
        if clientes.count() > 1:
            cliente_a_mantener = clientes.first()
            clientes_a_eliminar = clientes.exclude(id=cliente_a_mantener.id)
            count_eliminados = clientes_a_eliminar.count()
            clientes_a_eliminar.delete()
            duplicados_eliminados += count_eliminados
            print(f"Usuario {usuario.username}: eliminados {count_eliminados} clientes duplicados")
    
    print(f"Total duplicados eliminados: {duplicados_eliminados}")
    
    # 3. Crear clientes faltantes
    usuarios_sin_cliente = Usuario.objects.filter(rol='cliente', cliente__isnull=True)
    creados = 0
    for usuario in usuarios_sin_cliente:
        Cliente.objects.create(
            usuario=usuario,
            telefono='',
            direccion=''
        )
        creados += 1
        print(f"Cliente creado para usuario: {usuario.username}")
    
    print(f"Total clientes creados: {creados}")

print("=== RESUMEN FINAL ===")
print(f"Total usuarios: {Usuario.objects.count()}")
print(f"Total clientes: {Cliente.objects.count()}")
print(f"Usuarios rol 'cliente': {Usuario.objects.filter(rol='cliente').count()}")
print(f"Usuarios rol 'cliente' con cliente: {Usuario.objects.filter(rol='cliente', cliente__isnull=False).count()}")
print(f"Usuarios rol 'cliente' sin cliente: {Usuario.objects.filter(rol='cliente', cliente__isnull=True).count()}")
print("=== LIMPIEZA COMPLETADA ===")
