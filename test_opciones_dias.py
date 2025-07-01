#!/usr/bin/env python
"""
Prueba de las opciones de días para los productos
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from productos.models import Producto

def main():
    print("=== OPCIONES DE DÍAS POR PRODUCTO ===\n")
    
    productos = Producto.objects.all()
    
    for producto in productos:
        print(f"Producto: {producto.nombre}")
        print(f"  Precio diario: ${producto.precio_diario}")
        print(f"  Días mínimos: {producto.dias_minimos_renta}")
        
        opciones = producto.get_opciones_dias_renta()
        print(f"  Opciones de días disponibles: {opciones}")
        
        print(f"  Precio display: {producto.get_precio_display()}")
        print()

if __name__ == '__main__':
    main()
