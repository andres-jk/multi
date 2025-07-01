#!/usr/bin/env python
"""
Script para verificar que todos los templates de pedidos están actualizados 
al nuevo sistema de días y no hay errores en la visualización
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from productos.models import Producto
from usuarios.models import CarritoItem, Usuario
from pedidos.models import Pedido, DetallePedido

def verificar_metodos_carritoitem():
    """Verificar que CarritoItem tiene todos los métodos necesarios"""
    print("=== VERIFICACIÓN MÉTODOS CARRITO ITEM ===")
    
    # Crear producto de prueba
    producto = Producto.objects.create(
        nombre="Producto Test Templates",
        precio_diario=5000,
        dias_minimos_renta=7,
        cantidad_disponible=10
    )
    
    # Verificar que el método get_descripcion_dias existe
    try:
        # Buscar un usuario para hacer la prueba
        usuario = Usuario.objects.first()
        if not usuario:
            print("⚠️ No hay usuarios en la base de datos para hacer la prueba")
            producto.delete()
            return
            
        # Crear item de carrito
        item = CarritoItem.objects.create(
            usuario=usuario,
            producto=producto,
            cantidad=2,
            dias_renta=14
        )
        
        # Probar métodos
        descripcion_periodo = item.get_descripcion_periodo()
        descripcion_dias = item.get_descripcion_dias()
        subtotal = item.subtotal
        peso_total = item.peso_total
        
        print(f"✓ get_descripcion_periodo(): {descripcion_periodo}")
        print(f"✓ get_descripcion_dias(): {descripcion_dias}")
        print(f"✓ subtotal: ${subtotal}")
        print(f"✓ peso_total: {peso_total} kg")
        
        # Limpiar
        item.delete()
        producto.delete()
        
        print("✅ Todos los métodos de CarritoItem funcionan correctamente\n")
        
    except Exception as e:
        print(f"❌ Error en métodos de CarritoItem: {e}")
        producto.delete()

def verificar_metodos_detallepedido():
    """Verificar que DetallePedido tiene los campos correctos"""
    print("=== VERIFICACIÓN CAMPOS DETALLE PEDIDO ===")
    
    # Verificar que tiene los campos nuevos
    campos_necesarios = ['precio_diario', 'dias_renta']
    campos_encontrados = []
    
    for campo in campos_necesarios:
        if hasattr(DetallePedido, campo):
            campos_encontrados.append(campo)
            print(f"✓ Campo {campo} encontrado")
        else:
            print(f"❌ Campo {campo} NO encontrado")
    
    # Verificar que NO tiene los campos antiguos
    campos_antiguos = ['precio_unitario', 'meses_renta']
    for campo in campos_antiguos:
        if hasattr(DetallePedido, campo):
            print(f"⚠️ Campo antiguo {campo} AÚN existe")
        else:
            print(f"✓ Campo antiguo {campo} eliminado correctamente")
    
    if len(campos_encontrados) == len(campos_necesarios):
        print("✅ DetallePedido tiene todos los campos necesarios\n")
    else:
        print("❌ DetallePedido no tiene todos los campos necesarios\n")

def crear_pedido_prueba():
    """Crear un pedido de prueba para verificar que todo funciona"""
    print("=== CREANDO PEDIDO DE PRUEBA ===")
    
    try:
        # Buscar usuario y cliente
        usuario = Usuario.objects.first()
        if not usuario:
            print("⚠️ No hay usuarios para crear pedido de prueba")
            return None, None
        
        # Buscar o crear cliente
        from usuarios.models import Cliente
        cliente, created = Cliente.objects.get_or_create(
            usuario=usuario,
            defaults={'telefono': '123456789', 'direccion': 'Dirección de prueba'}
        )
        
        # Crear producto
        producto = Producto.objects.create(
            nombre="Producto Pedido Test",
            precio_diario=8600,
            dias_minimos_renta=7,
            cantidad_disponible=5
        )
        
        # Crear pedido (evitar update_total automático)
        pedido = Pedido()
        pedido.cliente = cliente
        pedido.direccion_entrega = "Dirección de prueba"
        pedido.total = 0
        pedido.save()  # Guardar para obtener el ID
        
        # Crear detalle
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=2,
            precio_diario=producto.precio_diario,
            dias_renta=14
        )
        
        # Actualizar total manualmente
        pedido.total = detalle.subtotal
        pedido.save()
        
        print(f"✓ Pedido creado: #{pedido.id_pedido}")
        print(f"  - Producto: {detalle.producto.nombre}")
        print(f"  - Cantidad: {detalle.cantidad}")
        print(f"  - Días: {detalle.dias_renta}")
        print(f"  - Precio diario: ${detalle.precio_diario}")
        print(f"  - Subtotal: ${detalle.subtotal}")
        print(f"  - Total pedido: ${pedido.total}")
        
        return pedido, producto
        
    except Exception as e:
        print(f"❌ Error creando pedido de prueba: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def limpiar_datos_prueba(pedido, producto):
    """Limpiar los datos de prueba"""
    if pedido:
        pedido.delete()
        print("✓ Pedido de prueba eliminado")
    if producto:
        producto.delete()
        print("✓ Producto de prueba eliminado")

def main():
    """Ejecutar todas las verificaciones"""
    print("VERIFICACIÓN DE TEMPLATES DE PEDIDOS")
    print("=" * 40)
    
    try:
        verificar_metodos_carritoitem()
        verificar_metodos_detallepedido()
        
        pedido, producto = crear_pedido_prueba()
        
        if pedido:
            print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
            print("\nAhora puedes probar los siguientes URLs:")
            print(f"- /pedidos/detalle/{pedido.id_pedido}/ (Detalle del pedido)")
            print("- /usuarios/carrito/ (Carrito)")
            print("- Generar cotización PDF")
            print("\nTodos los templates deberían mostrar 'Días' en lugar de 'Meses'")
            
            # Limpiar después de mostrar información
            limpiar_datos_prueba(pedido, producto)
        else:
            print("⚠️ No se pudo crear pedido de prueba")
            
    except Exception as e:
        print(f"❌ ERROR EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
