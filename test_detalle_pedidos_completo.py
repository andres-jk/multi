#!/usr/bin/env python
"""
Script para verificar que los clientes pueden ver correctamente los detalles de sus pedidos
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from pedidos.models import Pedido, DetallePedido
from usuarios.models import Usuario, Cliente
from productos.models import Producto

def verificar_pedidos_con_detalles():
    """Verificar que hay pedidos con detalles y que los campos son correctos"""
    print("=== VERIFICACIÓN PEDIDOS CON DETALLES ===")
    
    pedidos_con_detalles = Pedido.objects.filter(detalles__isnull=False).distinct()
    print(f"Pedidos con detalles: {pedidos_con_detalles.count()}")
    
    for pedido in pedidos_con_detalles[:3]:
        print(f"\n📦 Pedido #{pedido.id_pedido}")
        print(f"   Cliente: {pedido.cliente}")
        
        if pedido.cliente and pedido.cliente.usuario:
            print(f"   Usuario: {pedido.cliente.usuario.username}")
            print(f"   🔗 URL cliente: /pedidos/mis-pedidos/{pedido.id_pedido}/")
        
        detalles = pedido.detalles.all()
        print(f"   Detalles: {detalles.count()}")
        
        for detalle in detalles:
            print(f"     • {detalle.producto.nombre}")
            print(f"       Cantidad: {detalle.cantidad}")
            print(f"       Días: {detalle.dias_renta}")
            print(f"       Precio diario: ${detalle.precio_diario}")
            print(f"       Subtotal: ${detalle.subtotal}")
            
            # Verificar que los campos nuevos existen
            try:
                assert hasattr(detalle, 'precio_diario'), "Campo precio_diario no existe"
                assert hasattr(detalle, 'dias_renta'), "Campo dias_renta no existe"
                assert not hasattr(detalle, 'precio_unitario'), "Campo precio_unitario aún existe"
                assert not hasattr(detalle, 'meses_renta'), "Campo meses_renta aún existe"
                print(f"       ✅ Campos correctos")
            except AssertionError as e:
                print(f"       ❌ Error: {e}")

def verificar_templates_actualizados():
    """Verificar que los templates están actualizados"""
    print("\n=== VERIFICACIÓN TEMPLATES ===")
    
    templates_actualizados = [
        'pedidos/detalle_mi_pedido.html',
        'pedidos/detalle_pedido.html',
        'usuarios/detalle_pedido.html',
        'usuarios/pago.html',
        'usuarios/confirmacion_pago.html',
        'usuarios/pago_recibo.html',
        'usuarios/ver_remision.html'
    ]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for template_path in templates_actualizados:
        # Construir la ruta completa del template
        if template_path.startswith('pedidos/'):
            full_path = os.path.join(base_path, 'pedidos', 'templates', template_path)
        else:
            full_path = os.path.join(base_path, 'usuarios', 'templates', template_path)
        
        if os.path.exists(full_path):
            # Leer el contenido del template
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar que no contenga referencias al sistema antiguo
            has_meses = 'meses_renta' in content.lower() or '>meses<' in content.lower()
            has_precio_unitario = 'precio_unitario' in content.lower()
            has_dias = 'dias_renta' in content.lower() or '>días<' in content.lower()
            has_precio_diario = 'precio_diario' in content.lower()
            
            print(f"📄 {template_path}:")
            if has_meses or has_precio_unitario:
                print(f"   ⚠️ Aún contiene referencias al sistema antiguo")
                if has_meses:
                    print(f"      - Contiene 'meses'")
                if has_precio_unitario:
                    print(f"      - Contiene 'precio_unitario'")
            else:
                print(f"   ✅ Limpio de referencias antiguas")
                
            if has_dias and has_precio_diario:
                print(f"   ✅ Contiene campos del nuevo sistema")
            else:
                print(f"   ⚠️ No contiene todos los campos nuevos")
        else:
            print(f"📄 {template_path}: ❌ No encontrado")

def crear_url_ejemplo():
    """Mostrar URLs de ejemplo para probar"""
    print("\n=== URLS PARA PROBAR ===")
    
    # Buscar un pedido con detalles
    pedido_con_detalles = Pedido.objects.filter(detalles__isnull=False).first()
    
    if pedido_con_detalles and pedido_con_detalles.cliente and pedido_con_detalles.cliente.usuario:
        usuario = pedido_con_detalles.cliente.usuario
        pedido_id = pedido_con_detalles.id_pedido
        
        print(f"🎯 Para probar como cliente '{usuario.username}':")
        print(f"   1. Iniciar sesión como: {usuario.username}")
        print(f"   2. Ir a: http://127.0.0.1:8000/pedidos/mis-pedidos/{pedido_id}/")
        print(f"   3. Deberías ver los productos con días y precio diario")
        print()
        print(f"🎯 Para probar como admin:")
        print(f"   1. Ir a: http://127.0.0.1:8000/pedidos/{pedido_id}/")
        print(f"   2. Deberías ver todos los detalles del pedido")
    else:
        print("⚠️ No hay pedidos con detalles para probar")

def main():
    """Ejecutar todas las verificaciones"""
    print("VERIFICACIÓN COMPLETA - DETALLES DE PEDIDOS")
    print("=" * 50)
    
    try:
        verificar_pedidos_con_detalles()
        verificar_templates_actualizados()
        crear_url_ejemplo()
        
        print("\n" + "=" * 50)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("\nSi todo está correcto, los clientes deberían poder:")
        print("• Ver los detalles de sus pedidos sin errores")
        print("• Ver productos listados con días y precio diario") 
        print("• Generar PDFs de cotización y remisión")
        print("• Navegar por toda la interfaz sin errores")
        
    except Exception as e:
        print(f"❌ ERROR EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
