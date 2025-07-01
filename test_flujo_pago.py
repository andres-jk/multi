#!/usr/bin/env python
"""
Script para probar el flujo de pago y verificar que las URLs funcionan
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from usuarios.models import Usuario, Cliente
from pedidos.models import Pedido

def test_urls_pago():
    """Probar que todas las URLs relacionadas con pagos funcionen"""
    print("=== TEST DE URLs DE PAGO ===\n")
    
    urls_to_test = [
        ('pedidos:mis_pedidos', {}, 'Lista de pedidos'),
        ('pedidos:detalle_mi_pedido', {'pedido_id': 30}, 'Detalle de pedido'),
        ('usuarios:procesar_pago', {'pedido_id': 30}, 'Procesar pago'),
        ('usuarios:login', {}, 'Login'),
        ('usuarios:inicio_cliente', {}, 'Inicio cliente'),
    ]
    
    for url_name, kwargs, description in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {description}: {url}")
        except NoReverseMatch as e:
            print(f"❌ {description}: Error - {e}")
    
    print("\n=== TEST DE FLUJO DE PAGO ===\n")
    
    # Buscar un pedido existente para probar
    try:
        pedido = Pedido.objects.filter(
            cliente__isnull=False,
            estado_pedido_general='pendiente_pago'
        ).first()
        
        if pedido:
            print(f"📦 Pedido de prueba: #{pedido.id_pedido}")
            print(f"    Cliente: {pedido.cliente}")
            print(f"    Estado: {pedido.estado_pedido_general}")
            print(f"    Total: ${pedido.total}")
            
            # Probar URLs específicas
            try:
                url_procesar = reverse('usuarios:procesar_pago', kwargs={'pedido_id': pedido.id_pedido})
                print(f"✅ URL procesar pago: {url_procesar}")
            except NoReverseMatch as e:
                print(f"❌ Error URL procesar pago: {e}")
                
            try:
                url_detalle = reverse('pedidos:detalle_mi_pedido', kwargs={'pedido_id': pedido.id_pedido})
                print(f"✅ URL detalle pedido: {url_detalle}")
            except NoReverseMatch as e:
                print(f"❌ Error URL detalle pedido: {e}")
                
        else:
            print("⚠️  No hay pedidos pendientes de pago para probar")
            
            # Crear uno para probar
            pedido = Pedido.objects.filter(cliente__isnull=False).first()
            if pedido:
                print(f"📦 Usando pedido existente: #{pedido.id_pedido}")
                
                try:
                    url_procesar = reverse('usuarios:procesar_pago', kwargs={'pedido_id': pedido.id_pedido})
                    print(f"✅ URL procesar pago: {url_procesar}")
                except NoReverseMatch as e:
                    print(f"❌ Error URL procesar pago: {e}")
            
    except Exception as e:
        print(f"❌ Error al buscar pedidos: {e}")

def test_client_flow():
    """Probar el flujo completo del cliente"""
    print("\n=== TEST DE FLUJO DEL CLIENTE ===\n")
    
    client = Client()
    
    # URLs que un cliente típicamente visitaría
    client_urls = [
        ('/', 'Página principal'),
        ('/usuarios/login/', 'Login'),
        ('/usuarios/registro/', 'Registro'),
        ('/panel/mis-pedidos/', 'Mis pedidos (requiere login)'),
    ]
    
    for url, description in client_urls:
        try:
            response = client.get(url)
            status = "✅" if response.status_code in [200, 302] else "❌"
            print(f"{status} {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")

if __name__ == "__main__":
    test_urls_pago()
    test_client_flow()
    print("\n✅ PRUEBAS COMPLETADAS")
