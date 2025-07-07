#!/usr/bin/env python3
"""
Prueba Final con Datos Reales del Sistema
Verifica que la generación de cotización PDF funcione con datos reales
2025-01-06
"""

import os
import sys
import django
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

# Configurar Django
os.chdir(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from usuarios.models import Cliente, CarritoItem
from productos.models import Producto
from usuarios.views import _generate_common_pdf
from decimal import Decimal
import traceback

User = get_user_model()

def setup_test_data():
    """Configura datos de prueba realistas"""
    print("Configurando datos de prueba...")
    
    # Crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_real_user',
        defaults={
            'email': 'test@multiandamios.com',
            'first_name': 'Carlos',
            'last_name': 'Pérez',
            'password': 'testpass123'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Usuario creado")
    else:
        print("✅ Usuario existente encontrado")
    
    # Crear cliente asociado
    cliente, created = Cliente.objects.get_or_create(
        usuario=user,
        defaults={
            'telefono': '301-555-0123',
            'direccion': 'Calle 123 #45-67, Bogotá'
        }
    )
    
    if created:
        print("✅ Cliente creado")
    else:
        print("✅ Cliente existente encontrado")
    
    # Crear productos de prueba
    productos_data = [
        {
            'nombre': 'Andamio Metálico 2x1.5m',
            'descripcion': 'Andamio metálico resistente para construcción',
            'precio_diario': Decimal('25000.00'),
            'peso': Decimal('45.50'),
            'cantidad_disponible': 50
        },
        {
            'nombre': 'Escalera de Aluminio 3m',
            'descripcion': 'Escalera telescópica de aluminio',
            'precio_diario': Decimal('15000.00'),
            'peso': Decimal('8.20'),
            'cantidad_disponible': 20
        },
        {
            'nombre': 'Plataforma de Trabajo',
            'descripcion': 'Plataforma de trabajo con barandas',
            'precio_diario': Decimal('35000.00'),
            'peso': Decimal('65.00'),
            'cantidad_disponible': 15
        }
    ]
    
    productos_creados = []
    for data in productos_data:
        producto, created = Producto.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data
        )
        productos_creados.append(producto)
        if created:
            print(f"✅ Producto creado: {producto.nombre}")
    
    # Limpiar carrito existente
    CarritoItem.objects.filter(usuario=user).delete()
    
    # Crear items de carrito
    items_data = [
        {'producto': productos_creados[0], 'cantidad': 10, 'dias_renta': 15},
        {'producto': productos_creados[1], 'cantidad': 5, 'dias_renta': 7},
        {'producto': productos_creados[2], 'cantidad': 3, 'dias_renta': 30}
    ]
    
    for item_data in items_data:
        CarritoItem.objects.create(
            usuario=user,
            producto=item_data['producto'],
            cantidad=item_data['cantidad'],
            dias_renta=item_data['dias_renta']
        )
        print(f"✅ Item agregado: {item_data['cantidad']}x {item_data['producto'].nombre}")
    
    return user

def add_middleware_to_request(request):
    """Agrega middleware necesario al request"""
    # Session middleware
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()
    
    # Messages middleware
    message_middleware = MessageMiddleware(lambda req: None)
    message_middleware.process_request(request)

def test_real_cotizacion_generation():
    """Prueba la generación real de cotización PDF"""
    print("\n=== PRUEBA DE GENERACIÓN REAL DE COTIZACIÓN ===")
    
    try:
        # Configurar datos
        user = setup_test_data()
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.get('/cotizacion')
        request.user = user
        
        # Agregar middleware necesario
        add_middleware_to_request(request)
        
        # Obtener items del carrito
        items_carrito = CarritoItem.objects.filter(usuario=user)
        
        if not items_carrito.exists():
            print("❌ No hay items en el carrito")
            return False
        
        print(f"✅ {items_carrito.count()} items encontrados en el carrito")
        
        # Generar PDF
        print("Generando PDF...")
        response = _generate_common_pdf(request, 'cotizacion', items_carrito)
        
        # Verificar respuesta
        if response.status_code == 200:
            print("✅ PDF generado exitosamente")
            print(f"   Content-Type: {response.get('Content-Type')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Verificar que el contenido es realmente un PDF
            pdf_header = response.content[:4]
            if pdf_header == b'%PDF':
                print("✅ Contenido confirmado como PDF válido")
                return True
            else:
                print(f"❌ Contenido no es PDF válido. Header: {pdf_header}")
                return False
        else:
            print(f"❌ Error en respuesta. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación de PDF: {e}")
        traceback.print_exc()
        return False

def test_edge_cases():
    """Prueba casos edge con datos reales"""
    print("\n=== PRUEBA DE CASOS EDGE ===")
    
    try:
        user = User.objects.get(username='test_real_user')
        
        # Caso 1: Producto sin precio
        producto_sin_precio = Producto.objects.create(
            nombre='Producto Sin Precio',
            descripcion='Producto de prueba sin precio',
            precio_diario=None,  # Precio None
            cantidad_disponible=10
        )
        
        CarritoItem.objects.create(
            usuario=user,
            producto=producto_sin_precio,
            cantidad=1,
            dias_renta=5
        )
        
        factory = RequestFactory()
        request = factory.get('/cotizacion')
        request.user = user
        add_middleware_to_request(request)
        
        items_carrito = CarritoItem.objects.filter(usuario=user)
        
        print("Probando con producto sin precio...")
        response = _generate_common_pdf(request, 'cotizacion', items_carrito)
        
        if response.status_code == 200:
            print("✅ Caso edge manejado correctamente (producto sin precio)")
        else:
            print("❌ Falló con producto sin precio")
            return False
        
        # Limpiar
        CarritoItem.objects.filter(producto=producto_sin_precio).delete()
        producto_sin_precio.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en casos edge: {e}")
        traceback.print_exc()
        return False

def run_real_system_test():
    """Ejecutar prueba completa del sistema real"""
    print("PRUEBA FINAL CON DATOS REALES DEL SISTEMA")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    try:
        # Test 1: Generación normal
        if test_real_cotizacion_generation():
            tests_passed += 1
            print("✅ GENERACIÓN NORMAL: PASADO")
        else:
            print("❌ GENERACIÓN NORMAL: FALLIDO")
        
        # Test 2: Casos edge
        if test_edge_cases():
            tests_passed += 1
            print("✅ CASOS EDGE: PASADO")
        else:
            print("❌ CASOS EDGE: FALLIDO")
        
        print("\n" + "=" * 50)
        print(f"RESULTADO: {tests_passed}/{total_tests} pruebas pasadas")
        
        if tests_passed == total_tests:
            print("🎉 SISTEMA REAL FUNCIONANDO PERFECTAMENTE")
            print("✅ Generación de PDF confirmada con datos reales")
            return True
        else:
            print("⚠️ ALGUNOS TESTS FALLARON")
            return False
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN PRUEBA: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_real_system_test()
