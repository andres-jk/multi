#!/usr/bin/env python
"""
Script para probar la creación de productos con el nuevo sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from productos.models import Producto

def test_crear_productos():
    """Prueba la creación de productos con diferentes tipos de renta"""
    print("🧪 Probando creación de productos...")
    
    # Crear producto mensual
    producto_mensual = Producto.objects.create(
        nombre="Producto Test Mensual",
        descripcion="Producto de prueba para renta mensual",
        precio=1000.00,
        tipo_renta="mensual",
        cantidad_disponible=10
    )
    
    print(f"✅ Producto mensual creado:")
    print(f"   - Nombre: {producto_mensual.nombre}")
    print(f"   - Tipo: {producto_mensual.get_tipo_renta_display()}")
    print(f"   - Precio mensual: ${producto_mensual.precio}")
    print(f"   - Precio semanal: ${producto_mensual.precio_semanal}")
    
    # Crear producto semanal
    producto_semanal = Producto.objects.create(
        nombre="Producto Test Semanal",
        descripcion="Producto de prueba para renta semanal",
        precio=800.00,
        precio_semanal=220.00,
        tipo_renta="semanal",
        cantidad_disponible=5
    )
    
    print(f"✅ Producto semanal creado:")
    print(f"   - Nombre: {producto_semanal.nombre}")
    print(f"   - Tipo: {producto_semanal.get_tipo_renta_display()}")
    print(f"   - Precio mensual: ${producto_semanal.precio}")
    print(f"   - Precio semanal: ${producto_semanal.precio_semanal}")
    
    # Probar métodos
    print(f"\n🔍 Probando métodos:")
    print(f"   - Precio por tipo (mensual): ${producto_mensual.get_precio_por_tipo('mensual')}")
    print(f"   - Precio por tipo (semanal): ${producto_mensual.get_precio_por_tipo('semanal')}")
    print(f"   - Precio por tipo (semanal): ${producto_semanal.get_precio_por_tipo('semanal')}")
    
    # Limpiar productos de prueba
    producto_mensual.delete()
    producto_semanal.delete()
    print(f"\n🧹 Productos de prueba eliminados")
    
    print(f"\n🎉 Prueba completada exitosamente!")

if __name__ == "__main__":
    test_crear_productos()
