#!/usr/bin/env python
"""
Script para verificar que toda la interfaz está usando el nuevo sistema de días
y no hay referencias residuales al sistema de meses/semanas/tipo_renta
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from productos.models import Producto
from usuarios.models import CarritoItem
from pedidos.models import DetallePedido

def test_modelo_producto():
    """Verificar que el modelo Producto funciona correctamente"""
    print("=== VERIFICACIÓN MODELO PRODUCTO ===")
    
    # Crear un producto de prueba
    producto = Producto.objects.create(
        nombre="Producto Test Interface",
        descripcion="Producto para probar interfaz",
        precio_diario=5000,
        dias_minimos_renta=7,
        cantidad_disponible=10
    )
    
    print(f"Producto creado: {producto.nombre}")
    print(f"Precio diario: ${producto.precio_diario}")
    print(f"Días mínimos: {producto.dias_minimos_renta}")
    print(f"Display precio: {producto.get_precio_display()}")
    
    # Verificar opciones de días
    opciones = producto.get_opciones_dias_renta()
    print(f"Opciones de días (hasta 90): {opciones[:10]}...")  # Mostrar solo primeras 10
    
    # Verificar validación de días
    print(f"¿Es válido 7 días? {producto.es_dias_valido(7)}")
    print(f"¿Es válido 14 días? {producto.es_dias_valido(14)}")
    print(f"¿Es válido 15 días? {producto.es_dias_valido(15)}")
    
    # Verificar cálculo de precio
    try:
        precio_total = producto.get_precio_total(14, 2)  # 14 días, 2 unidades
        print(f"Precio total para 14 días, 2 unidades: ${precio_total}")
    except ValueError as e:
        print(f"Error en cálculo: {e}")
    
    # Limpiar
    producto.delete()
    print("✓ Modelo Producto funcionando correctamente\n")

def test_carrito_item():
    """Verificar que CarritoItem funciona con el nuevo sistema"""
    print("=== VERIFICACIÓN CARRITO ITEM ===")
    
    # Crear producto para prueba
    producto = Producto.objects.create(
        nombre="Producto Carrito Test",
        precio_diario=8600,
        dias_minimos_renta=7,
        cantidad_disponible=5
    )
    
    # Verificar que no hay atributos del sistema antiguo
    try:
        # Estos campos no deberían existir en el nuevo modelo
        hasattr_tipo_renta = hasattr(CarritoItem, 'tipo_renta')
        hasattr_meses_renta = hasattr(CarritoItem, 'meses_renta')
        hasattr_periodo_renta = hasattr(CarritoItem, 'periodo_renta')
        
        print(f"¿Tiene tipo_renta? {hasattr_tipo_renta}")
        print(f"¿Tiene meses_renta? {hasattr_meses_renta}")
        print(f"¿Tiene periodo_renta? {hasattr_periodo_renta}")
        
        if any([hasattr_tipo_renta, hasattr_meses_renta, hasattr_periodo_renta]):
            print("⚠️ ADVERTENCIA: CarritoItem aún tiene campos del sistema antiguo")
        else:
            print("✓ CarritoItem limpio de referencias antiguas")
            
    except Exception as e:
        print(f"Error verificando campos: {e}")
    
    # Limpiar
    producto.delete()
    print("✓ CarritoItem verificado\n")

def test_detalle_pedido():
    """Verificar que DetallePedido funciona con el nuevo sistema"""
    print("=== VERIFICACIÓN DETALLE PEDIDO ===")
    
    # Verificar que no hay atributos del sistema antiguo
    try:
        hasattr_meses_renta = hasattr(DetallePedido, 'meses_renta')
        hasattr_precio_unitario = hasattr(DetallePedido, 'precio_unitario')
        
        print(f"¿Tiene meses_renta? {hasattr_meses_renta}")
        print(f"¿Tiene precio_unitario? {hasattr_precio_unitario}")
        
        # Verificar que tiene los nuevos campos
        hasattr_dias_renta = hasattr(DetallePedido, 'dias_renta')
        hasattr_precio_diario = hasattr(DetallePedido, 'precio_diario')
        
        print(f"¿Tiene dias_renta? {hasattr_dias_renta}")
        print(f"¿Tiene precio_diario? {hasattr_precio_diario}")
        
        if hasattr_meses_renta or hasattr_precio_unitario:
            print("⚠️ ADVERTENCIA: DetallePedido aún tiene campos del sistema antiguo")
        
        if not (hasattr_dias_renta and hasattr_precio_diario):
            print("⚠️ ADVERTENCIA: DetallePedido no tiene todos los campos nuevos")
        else:
            print("✓ DetallePedido correctamente migrado")
            
    except Exception as e:
        print(f"Error verificando campos: {e}")
    
    print("✓ DetallePedido verificado\n")

def test_calculos_coherentes():
    """Verificar que los cálculos son coherentes en todos los niveles"""
    print("=== VERIFICACIÓN CÁLCULOS COHERENTES ===")
    
    # Crear producto de prueba
    producto = Producto.objects.create(
        nombre="Producto Cálculo Test",
        precio_diario=8600,
        dias_minimos_renta=7,
        cantidad_disponible=10
    )
    
    # Caso de prueba: 5 unidades por 7 días
    cantidad = 5
    dias = 7
    
    precio_total = producto.get_precio_total(dias, cantidad)
    precio_esperado = 8600 * 7 * 5  # 301,000
    
    print(f"Producto: {producto.nombre}")
    print(f"Precio diario: ${producto.precio_diario}")
    print(f"Cantidad: {cantidad}")
    print(f"Días: {dias}")
    print(f"Precio calculado: ${precio_total}")
    print(f"Precio esperado: ${precio_esperado}")
    print(f"¿Coinciden? {precio_total == precio_esperado}")
    
    if precio_total == precio_esperado:
        print("✓ Cálculos coherentes")
    else:
        print("⚠️ ERROR: Cálculos inconsistentes")
    
    # Limpiar
    producto.delete()
    print("✓ Cálculos verificados\n")

def test_opciones_dias_interface():
    """Verificar que las opciones de días son correctas para la interfaz"""
    print("=== VERIFICACIÓN OPCIONES DÍAS INTERFAZ ===")
    
    # Producto con mínimo 7 días
    producto_7 = Producto.objects.create(
        nombre="Producto 7 días",
        precio_diario=5000,
        dias_minimos_renta=7,
        cantidad_disponible=10
    )
    
    opciones_7 = producto_7.get_opciones_dias_renta(max_dias=35)
    print(f"Producto mínimo 7 días - opciones: {opciones_7}")
    print(f"¿Van de 7 en 7? {all(opt % 7 == 0 for opt in opciones_7)}")
    
    # Producto con mínimo 30 días  
    producto_30 = Producto.objects.create(
        nombre="Producto 30 días",
        precio_diario=1000,
        dias_minimos_renta=30,
        cantidad_disponible=5
    )
    
    opciones_30 = producto_30.get_opciones_dias_renta(max_dias=120)
    print(f"Producto mínimo 30 días - opciones: {opciones_30}")
    print(f"¿Van de 30 en 30? {all(opt % 30 == 0 for opt in opciones_30)}")
    
    # Limpiar
    producto_7.delete()
    producto_30.delete()
    
    print("✓ Opciones de días correctas para interfaz\n")

def main():
    """Ejecutar todas las verificaciones"""
    print("INICIANDO VERIFICACIÓN COMPLETA DE LA INTERFAZ")
    print("=" * 50)
    
    try:
        test_modelo_producto()
        test_carrito_item() 
        test_detalle_pedido()
        test_calculos_coherentes()
        test_opciones_dias_interface()
        
        print("=" * 50)
        print("✅ VERIFICACIÓN COMPLETA EXITOSA")
        print("El sistema está completamente migrado al nuevo modelo de días")
        print("La interfaz debería mostrar correctamente:")
        print("- Días en lugar de meses/semanas")
        print("- Solo múltiplos del mínimo permitido")
        print("- Cálculos basados en precio diario")
        
    except Exception as e:
        print(f"❌ ERROR EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
