#!/usr/bin/env python
"""
Script simple para verificar pedidos con detalles
"""
import os
import sys
import django

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Cliente
from pedidos.models import Pedido, DetallePedido
from productos.models import Producto

def verificar_pedidos_con_detalles():
    """Verificar pedidos que tienen detalles"""
    print("=== VERIFICACIÓN DE PEDIDOS CON DETALLES ===\n")
    
    # Buscar pedidos que tienen detalles
    pedidos_con_detalles = Pedido.objects.filter(
        detalles__isnull=False
    ).distinct().select_related('cliente__usuario')
    
    print(f"📊 Total de pedidos con detalles: {pedidos_con_detalles.count()}")
    
    for pedido in pedidos_con_detalles[:5]:  # Solo los primeros 5
        print(f"\n📦 Pedido #{pedido.id_pedido}")
        print(f"    Cliente: {pedido.cliente}")
        print(f"    Estado: {pedido.estado_pedido_general}")
        print(f"    Fecha: {pedido.fecha}")
        print(f"    Total: ${pedido.total}")
        
        detalles = pedido.detalles.all()
        print(f"    📝 Detalles ({detalles.count()}):")
        
        for detalle in detalles:
            print(f"        - {detalle.producto.nombre}")
            print(f"          Cantidad: {detalle.cantidad}")
            
            # Verificar campos nuevos
            if hasattr(detalle, 'dias_renta'):
                print(f"          Días: {detalle.dias_renta}")
            else:
                print("          ❌ No tiene dias_renta")
                
            if hasattr(detalle, 'precio_diario'):
                print(f"          Precio diario: ${detalle.precio_diario}")
            else:
                print("          ❌ No tiene precio_diario")
                
            print(f"          Subtotal: ${detalle.subtotal}")
    
    return pedidos_con_detalles.first() if pedidos_con_detalles.exists() else None

def test_template_directo():
    """Test directo del template con un pedido válido"""
    print("\n=== TEST DIRECTO DEL TEMPLATE ===\n")
    
    pedido = verificar_pedidos_con_detalles()
    if not pedido:
        print("❌ No hay pedidos con detalles para probar")
        return
    
    # Simular contexto de template
    from django.template import Template, Context
    
    template_content = """
Pedido #{{ pedido.id_pedido }}
Cliente: {{ pedido.cliente }}
Total: ${{ pedido.total }}

Detalles:
{% for detalle in pedido.detalles.all %}
- {{ detalle.producto.nombre }}: {{ detalle.cantidad }} x {{ detalle.dias_renta }} días
  Precio diario: ${{ detalle.precio_diario }}
  Subtotal: ${{ detalle.subtotal }}
{% endfor %}
"""
    
    context = {
        'pedido': pedido,
    }
    
    template = Template(template_content)
    try:
        resultado = template.render(Context(context))
        print("✅ Template renderizado exitosamente:")
        print(resultado)
        
        # Verificar que contiene los datos esperados
        if str(pedido.id_pedido) in resultado:
            print("✅ ID del pedido aparece")
        if pedido.detalles.first() and pedido.detalles.first().producto.nombre in resultado:
            print("✅ Nombre del producto aparece")
        
    except Exception as e:
        print(f"❌ Error al renderizar: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_directo()
