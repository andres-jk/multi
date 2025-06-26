#!/usr/bin/env python
"""
Script de prueba para verificar el sistema de renta mensual/semanal
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import CarritoItem, Usuario
from productos.models import Producto
from django.contrib.auth import get_user_model

def test_sistema_renta():
    """Prueba básica del sistema de renta"""
    print("🔧 Iniciando pruebas del sistema de renta...")
    
    # 1. Verificar que existan productos
    productos = Producto.objects.filter(activo=True)
    print(f"✅ Productos encontrados: {productos.count()}")
    
    productos_lista = list(productos[:3])
    for producto in productos_lista:
        print(f"   - {producto.nombre}")
        print(f"     Precio mensual: ${producto.precio}")
        print(f"     Precio semanal: ${producto.get_precio_por_tipo('semanal')}")
        
        # Verificar cálculo de precios
        precio_mensual = producto.get_precio_por_tipo('mensual')
        precio_semanal = producto.get_precio_por_tipo('semanal')
        
        assert precio_mensual == producto.precio, "Error en precio mensual"
        assert precio_semanal > 0, "Error en precio semanal"
        
        print(f"     ✅ Precios calculados correctamente")
    
    # 2. Verificar usuarios con carrito
    usuarios_con_carrito = Usuario.objects.filter(items_carrito__isnull=False).distinct()
    print(f"✅ Usuarios con items en carrito: {usuarios_con_carrito.count()}")
    
    for usuario in usuarios_con_carrito[:3]:
        items = CarritoItem.objects.filter(usuario=usuario)
        print(f"   - {usuario.username}: {items.count()} items")
        
        for item in items[:2]:
            print(f"     * {item.producto.nombre}")
            print(f"       Tipo: {item.tipo_renta}")
            print(f"       Período: {item.periodo_renta}")
            print(f"       Precio unitario: ${item.precio_unitario}")
            print(f"       Subtotal: ${item.subtotal}")
            
            # Verificar cálculos
            precio_esperado = item.producto.get_precio_por_tipo(item.tipo_renta)
            subtotal_esperado = precio_esperado * item.periodo_renta * item.cantidad
            
            assert abs(item.precio_unitario - precio_esperado) < 0.01, "Error en precio unitario"
            assert abs(item.subtotal - subtotal_esperado) < 0.01, "Error en subtotal"
            
            print(f"       ✅ Cálculos correctos")
    
    # 3. Prueba de tipos de renta
    print("\n🧪 Probando tipos de renta...")
    
    if productos_lista:
        producto = productos_lista[0]
        
        # Crear item con renta mensual
        print(f"Producto de prueba: {producto.nombre}")
        print(f"Precio mensual: ${producto.get_precio_por_tipo('mensual')}")
        print(f"Precio semanal: ${producto.get_precio_por_tipo('semanal')}")
        
        # Verificar que el precio semanal sea aproximadamente 1/4 del mensual
        ratio = producto.get_precio_por_tipo('mensual') / producto.get_precio_por_tipo('semanal')
        print(f"Ratio mensual/semanal: {ratio:.2f}")
        
        if 3.5 <= ratio <= 4.5:  # Permitir un margen
            print("✅ Ratio de precios correcto")
        else:
            print("⚠️  Ratio de precios puede necesitar ajuste")
    
    print("\n🎉 Todas las pruebas completadas exitosamente!")
    print("\n📊 Resumen del sistema:")
    print(f"   - Productos activos: {Producto.objects.filter(activo=True).count()}")
    print(f"   - Items en carritos: {CarritoItem.objects.count()}")
    print(f"   - Tipos de renta soportados: Mensual, Semanal")

if __name__ == "__main__":
    test_sistema_renta()
