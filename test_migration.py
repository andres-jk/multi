#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("Ejecutando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'migrate', 'recibos'])
        print("Migraciones completadas exitosamente.")
    except Exception as e:
        print(f"Error al ejecutar migraciones: {e}")
        
    # Verificar si la tabla existe
    try:
        from recibos.models import EstadoProductoIndividual
        count = EstadoProductoIndividual.objects.count()
        print(f"Tabla EstadoProductoIndividual existe. Registros: {count}")
    except Exception as e:
        print(f"Error al acceder a EstadoProductoIndividual: {e}")
