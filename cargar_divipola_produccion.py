#!/usr/bin/env python
"""
Script para cargar datos de DIVIPOLA en producción
Ejecutar en PythonAnywhere: python3.10 cargar_divipola_produccion.py
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import Departamento, Municipio

def main():
    print("=== CARGA DE DATOS DIVIPOLA EN PRODUCCIÓN ===")
    
    # Verificar estado actual
    dept_count = Departamento.objects.count()
    muni_count = Municipio.objects.count()
    
    print(f"Estado actual:")
    print(f"- Departamentos: {dept_count}")
    print(f"- Municipios: {muni_count}")
    
    if dept_count == 0 or muni_count == 0:
        print("\n🔄 Cargando datos de DIVIPOLA...")
        try:
            call_command('loaddata', 'usuarios/fixtures/divipola_data.json')
            print("✅ Datos cargados exitosamente!")
            
            # Verificar nuevamente
            dept_count = Departamento.objects.count()
            muni_count = Municipio.objects.count()
            print(f"\nEstado final:")
            print(f"- Departamentos: {dept_count}")
            print(f"- Municipios: {muni_count}")
            
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
            return False
    else:
        print("✅ Los datos ya están cargados")
    
    print("\n=== VERIFICACIÓN DE DATOS ===")
    
    # Mostrar algunos ejemplos
    print("\nPrimeros 5 departamentos:")
    for dept in Departamento.objects.all()[:5]:
        print(f"- {dept.codigo}: {dept.nombre}")
    
    print("\nPrimeros 5 municipios:")
    for muni in Municipio.objects.all()[:5]:
        print(f"- {muni.codigo}: {muni.nombre} ({muni.departamento.nombre})")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
    else:
        print("\n❌ PROCESO FALLÓ")
        sys.exit(1)
