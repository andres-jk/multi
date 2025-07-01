#!/usr/bin/env python
"""
Script para probar la vista detalle_mi_pedido directamente
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import AnonymousUser

from django.contrib.auth.models import User
from usuarios.models import Cliente
from pedidos.models import Pedido, DetallePedido
from pedidos.views import detalle_mi_pedido
from django.urls import reverse

def test_vista_detalle_pedido():
    """Test de la vista detalle_mi_pedido"""
    print("=== TEST DE LA VISTA DETALLE_MI_PEDIDO ===\n")
    
    # Buscar un pedido con detalles
    pedido = Pedido.objects.filter(
        detalles__isnull=False
    ).select_related('cliente__usuario').first()
    
    if not pedido:
        print("❌ No hay pedidos con detalles")
        return
    
    print(f"📦 Testing con pedido #{pedido.id_pedido}")
    print(f"    Cliente: {pedido.cliente}")
    print(f"    Detalles: {pedido.detalles.count()}")
    
    # Crear request factory
    factory = RequestFactory()
    
    # Crear request GET
    url = f'/panel/mis-pedidos/{pedido.id_pedido}/'
    request = factory.get(url)
    request.user = pedido.cliente.usuario
    
    try:
        # Llamar la vista directamente
        from usuarios.decorators import cliente_required
        from django.http import HttpRequest
        
        # No podemos usar el decorador en tests, así que simulamos la función
        response = detalle_mi_pedido(request, pedido.id_pedido)
        
        print(f"✅ Vista ejecutada correctamente")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar que el contenido contiene elementos esperados
            if f"Pedido #{pedido.id_pedido}" in content:
                print("✅ Número de pedido en contenido")
            else:
                print("❌ Número de pedido NO en contenido")
            
            if "table" in content.lower():
                print("✅ Tabla presente en HTML")
            else:
                print("❌ Tabla NO presente en HTML")
            
            # Buscar nombres de productos
            primer_detalle = pedido.detalles.first()
            if primer_detalle and primer_detalle.producto.nombre in content:
                print("✅ Nombre del producto en contenido")
            else:
                print("❌ Nombre del producto NO en contenido")
            
            # Verificar datos de días y precio
            if "días" in content.lower():
                print("✅ Información de días presente")
            else:
                print("❌ Información de días NO presente")
            
            # Guardar el HTML para inspección
            with open(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios\debug_detalle_pedido.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("📄 HTML guardado en debug_detalle_pedido.html")
            
        else:
            print(f"❌ Error en la vista: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al ejecutar la vista: {e}")
        import traceback
        traceback.print_exc()

def test_servidor_directo():
    """Test usando el servidor de Django directamente"""
    print("\n=== TEST CON SERVIDOR DJANGO ===\n")
    
    # Buscar un pedido con detalles
    pedido = Pedido.objects.filter(
        detalles__isnull=False
    ).select_related('cliente__usuario').first()
    
    if not pedido:
        print("❌ No hay pedidos con detalles")
        return
    
    print(f"📦 Testing con pedido #{pedido.id_pedido}")
    print(f"    Usuario: {pedido.cliente.usuario.username}")
    
    # Verificar si el usuario puede hacer login
    user = pedido.cliente.usuario
    print(f"    Usuario activo: {user.is_active}")
    print(f"    Contraseña utilizable: {user.has_usable_password()}")
    
    # Info para login manual
    print(f"\n📋 Para probar manualmente:")
    print(f"    Usuario: {user.username}")
    print(f"    URL: /panel/mis-pedidos/{pedido.id_pedido}/")
    print(f"    Detalles esperados: {pedido.detalles.count()}")
    
    for detalle in pedido.detalles.all()[:3]:
        print(f"        - {detalle.producto.nombre}: {detalle.cantidad} x {detalle.dias_renta} días")

if __name__ == "__main__":
    test_vista_detalle_pedido()
    test_servidor_directo()
