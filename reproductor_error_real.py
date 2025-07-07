#!/usr/bin/env python3
"""
Reproductor de Error Real - Carrito Web
Simula exactamente la acción del usuario al presionar "GENERAR COTIZACIÓN PDF"
2025-01-06
"""

import os
import sys
import django
from django.conf import settings
import traceback

# Configurar Django
os.chdir(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from usuarios.models import Cliente, CarritoItem
from productos.models import Producto
from usuarios.views import generar_cotizacion_pdf

User = get_user_model()

def setup_real_user_scenario():
    """Configura un escenario real similar al del usuario"""
    print("🔍 CONFIGURANDO ESCENARIO REAL DEL USUARIO...")
    
    # Buscar usuario existente o crear uno
    user = User.objects.filter(username='testuser').first()
    if not user:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Prueba'
        )
        print(f"✅ Usuario creado: {user.username}")
    
    # Buscar o crear cliente
    cliente, created = Cliente.objects.get_or_create(
        usuario=user,
        defaults={
            'telefono': '123456789',
            'direccion': 'Dirección de prueba'
        }
    )
    
    # Limpiar carrito existente
    CarritoItem.objects.filter(usuario=user).delete()
    
    # Buscar productos existentes en la BD
    productos_existentes = Producto.objects.filter(activo=True)[:3]
    
    if not productos_existentes.exists():
        # Crear productos si no existen
        producto1 = Producto.objects.create(
            nombre='Andamio Metálico',
            precio_diario=25000,
            cantidad_disponible=10,
            dias_minimos_renta=7
        )
        producto2 = Producto.objects.create(
            nombre='Escalera Aluminio',
            precio_diario=15000,
            cantidad_disponible=5,
            dias_minimos_renta=7
        )
        productos_existentes = [producto1, producto2]
        print("✅ Productos creados")
    else:
        productos_existentes = list(productos_existentes)
        print(f"✅ Usando productos existentes: {len(productos_existentes)}")
    
    # Agregar productos al carrito
    for i, producto in enumerate(productos_existentes):
        CarritoItem.objects.create(
            usuario=user,
            producto=producto,
            cantidad=i + 1,
            dias_renta=(i + 1) * 7,  # 7, 14, 21 días
            precio_diario=producto.precio_diario
        )
    
    items_count = CarritoItem.objects.filter(usuario=user).count()
    print(f"✅ {items_count} items agregados al carrito")
    
    return user, cliente

def test_with_full_middleware():
    """Prueba con middleware completo como en una request real"""
    print("\n🌐 SIMULANDO REQUEST WEB REAL...")
    
    user, cliente = setup_real_user_scenario()
    
    # Usar el cliente de prueba de Django para simular una request web real
    client = Client()
    
    # Login del usuario
    client.force_login(user)
    
    try:
        print("📥 Enviando request a /usuarios/carrito/cotizacion-pdf/...")
        
        # Hacer la request real como lo haría el navegador
        response = client.get('/usuarios/carrito/cotizacion-pdf/')
        
        print(f"📤 Response Status: {response.status_code}")
        print(f"📤 Content-Type: {response.get('Content-Type', 'No Content-Type')}")
        
        if response.status_code == 200:
            print(f"✅ PDF generado exitosamente - Tamaño: {len(response.content)} bytes")
            
            # Verificar que sea un PDF válido
            if response.content.startswith(b'%PDF'):
                print("✅ Header PDF válido detectado")
                return True
            else:
                print(f"❌ Header inválido: {response.content[:20]}")
                return False
                
        elif response.status_code == 302:
            print(f"🔄 Redirect a: {response.get('Location', 'Unknown')}")
            return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Content: {response.content.decode('utf-8', errors='ignore')[:500]}")
            return False
            
    except Exception as e:
        print(f"💥 ERROR CAPTURADO: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        
        # Capturar el stacktrace completo
        print("\n📋 STACKTRACE COMPLETO:")
        traceback.print_exc()
        
        # Análisis específico del error
        if "'NoneType' object is not subscriptable" in str(e):
            print("\n🎯 ERROR DETECTADO: 'NoneType' object is not subscriptable'")
            analyze_none_type_error(e)
        
        return False

def analyze_none_type_error(error):
    """Analiza específicamente el error NoneType"""
    print("\n🔬 ANÁLISIS DEL ERROR:")
    
    # Obtener la línea exacta donde ocurre el error
    import traceback
    tb = traceback.format_exc()
    
    print("📍 Stacktrace del error:")
    lines = tb.split('\n')
    for i, line in enumerate(lines):
        if 'usuarios/views.py' in line or '_draw_products_table' in line:
            print(f"  🎯 {line}")
            if i + 1 < len(lines):
                print(f"     {lines[i + 1]}")

def test_with_request_factory():
    """Prueba con RequestFactory para debug más detallado"""
    print("\n🧪 PRUEBA CON REQUEST FACTORY...")
    
    user, cliente = setup_real_user_scenario()
    
    factory = RequestFactory()
    request = factory.get('/usuarios/carrito/cotizacion-pdf/')
    request.user = user
    
    # Agregar middleware necesario
    setattr(request, 'session', {})
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    try:
        print("🔧 Llamando directamente a generar_cotizacion_pdf...")
        response = generar_cotizacion_pdf(request)
        
        print(f"✅ Función ejecutada exitosamente")
        print(f"📤 Status: {getattr(response, 'status_code', 'No status')}")
        
        if hasattr(response, 'content'):
            print(f"📦 Content length: {len(response.content)}")
            if response.content.startswith(b'%PDF'):
                print("✅ PDF válido generado")
                return True
        
        return True
        
    except Exception as e:
        print(f"💥 ERROR EN REQUEST FACTORY: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Ejecuta prueba comprehensiva del error"""
    print("REPRODUCTOR DE ERROR REAL - CARRITO WEB")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Con middleware completo
    try:
        if test_with_full_middleware():
            success_count += 1
            print("✅ TEST MIDDLEWARE: PASADO")
        else:
            print("❌ TEST MIDDLEWARE: FALLIDO")
    except Exception as e:
        print(f"❌ TEST MIDDLEWARE: ERROR - {e}")
    
    # Test 2: Con RequestFactory
    try:
        if test_with_request_factory():
            success_count += 1
            print("✅ TEST REQUEST FACTORY: PASADO")
        else:
            print("❌ TEST REQUEST FACTORY: FALLIDO")
    except Exception as e:
        print(f"❌ TEST REQUEST FACTORY: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"RESULTADO: {success_count}/{total_tests} pruebas exitosas")
    
    if success_count == total_tests:
        print("🎉 ERROR NO REPRODUCIDO - Sistema funcionando")
    else:
        print("⚠️ ERROR CONFIRMADO - Requiere corrección adicional")
    
    return success_count == total_tests

if __name__ == "__main__":
    run_comprehensive_test()
