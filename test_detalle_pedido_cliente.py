#!/usr/bin/env python
"""
Script para verificar que el template de detalle de pedido para clientes funciona correctamente
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
from django.template.loader import render_to_string
from django.test import RequestFactory

def test_detalle_pedido_cliente():
    """Prueba que el template de detalle de pedido para cliente funciona"""
    print("=== TEST: DETALLE DE PEDIDO PARA CLIENTE ===\n")
    
    # Buscar un usuario cliente con pedidos
    cliente = Cliente.objects.filter(
        pedido__isnull=False
    ).select_related('usuario').first()
    
    if not cliente:
        print("❌ No se encontró ningún cliente con pedidos")
        return
    
    print(f"📋 Cliente encontrado: {cliente.usuario.username} ({cliente.usuario.first_name} {cliente.usuario.last_name})")
    
    # Obtener un pedido del cliente
    pedido = Pedido.objects.filter(cliente=cliente).first()
    if not pedido:
        print("❌ No se encontró ningún pedido para este cliente")
        return
    
    print(f"📦 Pedido: #{pedido.id_pedido} - Estado: {pedido.estado_pedido_general}")
    print(f"    Fecha: {pedido.fecha}")
    print(f"    Total: ${pedido.total}")
    
    # Verificar que tiene detalles
    detalles = pedido.detalles.all()
    print(f"📝 Detalles del pedido: {detalles.count()} productos")
    
    if detalles.count() == 0:
        print("❌ El pedido no tiene detalles")
        return
    
    for detalle in detalles:
        print(f"    - {detalle.producto.nombre}: {detalle.cantidad} unidades x {detalle.dias_renta} días")
        print(f"      Precio diario: ${detalle.precio_diario}, Subtotal: ${detalle.subtotal}")
    
    # Crear contexto similar al de la vista
    context = {
        'pedido': pedido,
        'detalles': detalles.select_related('producto'),
        'cliente': cliente,
        'request': None,  # Para el template base
        'user': cliente.usuario,  # Para el template base
    }
    
    # Intentar renderizar el template
    try:
        # Primero probamos solo la parte de la tabla
        template_content = """
        <table class="table">
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Días</th>
                    <th>Precio/Día</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {% for detalle in pedido.detalles.all %}
                <tr>
                    <td>{{ detalle.producto.nombre }}</td>
                    <td>{{ detalle.cantidad }}</td>
                    <td>{{ detalle.dias_renta }}</td>
                    <td>${{ detalle.precio_diario }}</td>
                    <td>${{ detalle.subtotal }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        """
        
        from django.template import Template, Context
        template = Template(template_content)
        rendered = template.render(Context(context))
        
        print("\n✅ Template renderizado exitosamente")
        print("📄 Contenido de la tabla:")
        print(rendered)
        
        # Verificar que el contenido contiene los datos esperados
        if pedido.detalles.first().producto.nombre in rendered:
            print("✅ Los datos del producto aparecen en el template")
        else:
            print("❌ Los datos del producto NO aparecen en el template")
        
        # Verificar si existen los campos nuevos
        primer_detalle = pedido.detalles.first()
        if hasattr(primer_detalle, 'dias_renta') and hasattr(primer_detalle, 'precio_diario'):
            print("✅ Los campos nuevos (dias_renta, precio_diario) existen")
        else:
            print("❌ Los campos nuevos NO existen")
            
    except Exception as e:
        print(f"❌ Error al renderizar el template: {e}")
        import traceback
        traceback.print_exc()

def test_url_detalle_pedido():
    """Prueba la URL y vista de detalle de pedido"""
    print("\n=== TEST: URL Y VISTA DE DETALLE ===\n")
    
    from django.urls import reverse
    from django.test import Client
    from django.contrib.auth import authenticate
    
    # Buscar un cliente con pedidos
    cliente = Cliente.objects.filter(pedido__isnull=False).first()
    if not cliente:
        print("❌ No hay clientes con pedidos")
        return
    
    pedido = Pedido.objects.filter(cliente=cliente).first()
    
    # Crear cliente de prueba
    client = Client()
    
    # Intentar acceder sin login
    url = reverse('pedidos:detalle_mi_pedido', kwargs={'pedido_id': pedido.id_pedido})
    print(f"🔗 URL: {url}")
    
    response = client.get(url)
    print(f"📊 Respuesta sin login: {response.status_code}")
    
    # Login y acceso
    client.force_login(cliente.usuario)
    response = client.get(url)
    print(f"📊 Respuesta con login: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ La vista funciona correctamente")
        
        # Verificar que el contexto contiene los datos necesarios
        if 'pedido' in response.context:
            print("✅ Variable 'pedido' en contexto")
        else:
            print("❌ Variable 'pedido' NO está en contexto")
            
        if 'detalles' in response.context:
            print("✅ Variable 'detalles' en contexto")
            detalles_count = response.context['detalles'].count()
            print(f"📝 Número de detalles en contexto: {detalles_count}")
        else:
            print("❌ Variable 'detalles' NO está en contexto")
            
        # Verificar contenido HTML
        content = response.content.decode('utf-8')
        if f"Pedido #{pedido.id_pedido}" in content:
            print("✅ El número de pedido aparece en el HTML")
        else:
            print("❌ El número de pedido NO aparece en el HTML")
            
        if "tabla" in content.lower() or "table" in content.lower():
            print("✅ Se encontró una tabla en el HTML")
        else:
            print("❌ NO se encontró tabla en el HTML")
            
    else:
        print(f"❌ Error en la vista: {response.status_code}")

if __name__ == "__main__":
    test_detalle_pedido_cliente()
    test_url_detalle_pedido()
