#!/usr/bin/env python
"""
Script para detectar y corregir TODOS los errores 'NoneType' object is not subscriptable
en el sistema de generación de PDFs
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Users\\andre\\OneDrive\\Documentos\\MultiAndamios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from usuarios.views import generar_cotizacion_pdf
from usuarios.models import CarritoItem

def analizar_errores_potenciales():
    """Analizar todos los posibles errores en el sistema de cotización"""
    print("=== ANÁLISIS DE ERRORES POTENCIALES ===")
    
    try:
        User = get_user_model()
        
        # 1. Verificar usuarios y carrito
        print("\n1. VERIFICANDO USUARIOS Y CARRITO:")
        users_with_items = User.objects.filter(items_carrito__isnull=False)
        print(f"   ✓ Usuarios con items en carrito: {users_with_items.count()}")
        
        if users_with_items.exists():
            user = users_with_items.first()
            print(f"   ✓ Usuario de prueba: {user.username}")
            
            # Verificar items del carrito
            items = CarritoItem.objects.filter(usuario=user)
            print(f"   ✓ Items del usuario: {items.count()}")
            
            for i, item in enumerate(items):
                print(f"   ✓ Item {i+1}:")
                print(f"      - ID: {item.id}")
                print(f"      - Producto: {item.producto}")
                print(f"      - Cantidad: {getattr(item, 'cantidad', 'MISSING')}")
                print(f"      - Subtotal: {getattr(item, 'subtotal', 'MISSING')}")
                
                # Verificar atributos críticos
                if not hasattr(item, 'producto') or item.producto is None:
                    print(f"      ❌ ERROR: Item sin producto!")
                    
                if not hasattr(item, 'cantidad') or item.cantidad is None:
                    print(f"      ❌ ERROR: Item sin cantidad!")
        
        # 2. Verificar estructura de datos en la función
        print("\n2. VERIFICANDO ESTRUCTURA DE DATOS:")
        headers = ["Descripción", "Cant.", "Período", "Precio Unit.", "Subtotal"]
        col_widths = [280, 50, 80, 80, 80]
        
        print(f"   ✓ Headers: {headers}")
        print(f"   ✓ Headers type: {type(headers)}")
        print(f"   ✓ Headers length: {len(headers) if headers else 'None'}")
        
        print(f"   ✓ Col_widths: {col_widths}")
        print(f"   ✓ Col_widths type: {type(col_widths)}")
        print(f"   ✓ Col_widths length: {len(col_widths) if col_widths else 'None'}")
        
        # Verificar que no hay elementos None
        for i, header in enumerate(headers):
            if header is None:
                print(f"      ❌ ERROR: Header {i} es None!")
                
        for i, width in enumerate(col_widths):
            if width is None:
                print(f"      ❌ ERROR: Col_width {i} es None!")
        
        # 3. Probar la función directamente
        print("\n3. PROBANDO FUNCIÓN DE COTIZACIÓN:")
        if users_with_items.exists():
            user = users_with_items.first()
            factory = RequestFactory()
            request = factory.get('/generar-cotizacion/')
            request.user = user
            
            try:
                response = generar_cotizacion_pdf(request)
                if response.status_code == 200:
                    print(f"   ✅ Función funcionando: Status {response.status_code}")
                    print(f"   ✅ Tamaño PDF: {len(response.content)} bytes")
                else:
                    print(f"   ❌ Error en función: Status {response.status_code}")
            except Exception as e:
                print(f"   ❌ ERROR EN FUNCIÓN: {e}")
                import traceback
                traceback.print_exc()
        
        # 4. Verificar funciones auxiliares
        print("\n4. VERIFICANDO FUNCIONES AUXILIARES:")
        from usuarios.views import _draw_products_table_v2, _generate_common_pdf
        
        print("   ✓ _generate_common_pdf: Importada correctamente")
        print("   ✓ _draw_products_table_v2: Importada correctamente")
        
        print("\n=== ANÁLISIS COMPLETADO ===")
        
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_errores_potenciales()
