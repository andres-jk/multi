"""
Migración personalizada para limpiar problemas de clientes
"""

from django.db import migrations
from django.db import transaction

def limpiar_clientes(apps, schema_editor):
    """
    Función para limpiar clientes duplicados y huérfanos
    """
    Usuario = apps.get_model('usuarios', 'Usuario')
    Cliente = apps.get_model('usuarios', 'Cliente')
    
    with transaction.atomic():
        # 1. Eliminar clientes huérfanos (sin usuario)
        clientes_huerfanos = Cliente.objects.filter(usuario__isnull=True)
        count_huerfanos = clientes_huerfanos.count()
        clientes_huerfanos.delete()
        print(f"Eliminados {count_huerfanos} clientes huérfanos")
        
        # 2. Eliminar duplicados de clientes
        duplicados_eliminados = 0
        for usuario in Usuario.objects.all():
            clientes = Cliente.objects.filter(usuario=usuario)
            if clientes.count() > 1:
                # Mantener el primer cliente, eliminar el resto
                cliente_a_mantener = clientes.first()
                clientes_a_eliminar = clientes.exclude(id=cliente_a_mantener.id)
                count_eliminados = clientes_a_eliminar.count()
                clientes_a_eliminar.delete()
                duplicados_eliminados += count_eliminados
                print(f"Usuario {usuario.username}: eliminados {count_eliminados} clientes duplicados")
        
        print(f"Total duplicados eliminados: {duplicados_eliminados}")
        
        # 3. Crear clientes para usuarios de rol 'cliente' que no tienen cliente
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

def revertir_limpieza(apps, schema_editor):
    """
    Función para revertir la limpieza (no hace nada)
    """
    pass

class Migration(migrations.Migration):
    
    dependencies = [
        ('usuarios', '0005_usuario_activo_usuario_puede_gestionar_clientes_and_more'),
    ]
    
    operations = [
        migrations.RunPython(limpiar_clientes, revertir_limpieza),
    ]
