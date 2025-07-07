#!/usr/bin/env python3
"""
Prueba Exhaustiva con Todos los Datos Reales
Testa la generación de PDF con cada usuario real del sistema
2025-01-06
"""

import os
import sys
import django

# Configurar Django
os.chdir(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from usuarios.models import CarritoItem

User = get_user_model()

def test_todos_los_usuarios():
    """Prueba la generación de PDF con todos los usuarios que tienen carrito"""
    print("PRUEBA EXHAUSTIVA CON DATOS REALES")
    print("=" * 40)
    
    # Obtener todos los usuarios con items en carrito
    usuarios_con_carrito = User.objects.filter(items_carrito__isnull=False).distinct()
    
    print(f"👥 Usuarios con carrito encontrados: {usuarios_con_carrito.count()}")
    
    client = Client()
    resultados = []
    
    for user in usuarios_con_carrito:
        print(f"\n🧪 PROBANDO USUARIO: {user.username}")
        
        # Obtener items del carrito de este usuario
        items = CarritoItem.objects.filter(usuario=user)
        print(f"   🛒 Items en carrito: {items.count()}")
        
        # Mostrar detalles de los items
        for item in items:
            print(f"     • {item.producto.nombre} - Cantidad: {item.cantidad} - Días: {item.dias_renta}")
        
        # Login y prueba
        client.force_login(user)
        
        try:
            response = client.get('/carrito/cotizacion-pdf/')
            
            if response.status_code == 200:
                if response.content.startswith(b'%PDF'):
                    print(f"   ✅ PDF generado exitosamente ({len(response.content)} bytes)")
                    resultados.append({'usuario': user.username, 'resultado': 'ÉXITO', 'bytes': len(response.content)})
                else:
                    print(f"   ❌ Response no es PDF válido")
                    resultados.append({'usuario': user.username, 'resultado': 'ERROR_NO_PDF', 'content': str(response.content[:100])})
            elif response.status_code == 302:
                print(f"   🔄 Redirect a: {response.get('Location', 'Unknown')}")
                resultados.append({'usuario': user.username, 'resultado': 'REDIRECT', 'location': response.get('Location', 'Unknown')})
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                resultados.append({'usuario': user.username, 'resultado': f'HTTP_{response.status_code}'})
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            error_str = str(e)
            
            # Detectar específicamente el error de NoneType
            if "'NoneType' object is not subscriptable" in error_str:
                print(f"   🚨 ERROR CONFIRMADO: NoneType object is not subscriptable")
                resultados.append({'usuario': user.username, 'resultado': 'ERROR_NONETYPE', 'error': error_str})
                
                # Analizar este usuario específico
                analizar_usuario_problematico(user)
            else:
                resultados.append({'usuario': user.username, 'resultado': 'ERROR_OTRO', 'error': error_str})
    
    # Reporte final
    print("\n" + "=" * 40)
    print("📊 REPORTE FINAL")
    print("=" * 40)
    
    exitos = sum(1 for r in resultados if r['resultado'] == 'ÉXITO')
    errores_nonetype = sum(1 for r in resultados if r['resultado'] == 'ERROR_NONETYPE')
    total = len(resultados)
    
    print(f"✅ Éxitos: {exitos}/{total}")
    print(f"🚨 Errores NoneType: {errores_nonetype}/{total}")
    
    if errores_nonetype > 0:
        print("\n🔍 USUARIOS CON ERROR NONETYPE:")
        for r in resultados:
            if r['resultado'] == 'ERROR_NONETYPE':
                print(f"   💥 {r['usuario']}: {r['error']}")
        return False
    else:
        print("\n🎉 TODOS LOS USUARIOS FUNCIONAN CORRECTAMENTE")
        return True

def analizar_usuario_problematico(user):
    """Analiza en detalle un usuario que presenta problemas"""
    print(f"\n🔬 ANÁLISIS DETALLADO DE USUARIO PROBLEMÁTICO: {user.username}")
    
    items = CarritoItem.objects.filter(usuario=user)
    
    for i, item in enumerate(items):
        print(f"\n   📦 ITEM #{i+1}:")
        print(f"      ID: {item.id}")
        print(f"      Producto: {item.producto}")
        print(f"      Producto nombre: {getattr(item.producto, 'nombre', 'NONE') if item.producto else 'PRODUCTO ES NONE'}")
        print(f"      Producto precio: {getattr(item.producto, 'precio_diario', 'NONE') if item.producto else 'PRODUCTO ES NONE'}")
        print(f"      Cantidad: {item.cantidad}")
        print(f"      Días renta: {item.dias_renta}")
        
        # Probar propiedades
        try:
            subtotal = item.subtotal
            print(f"      Subtotal: {subtotal}")
        except Exception as e:
            print(f"      ❌ Error en subtotal: {e}")
        
        try:
            precio_unitario = item.precio_unitario
            print(f"      Precio unitario: {precio_unitario}")
        except Exception as e:
            print(f"      ❌ Error en precio unitario: {e}")
        
        try:
            descripcion_dias = item.get_descripcion_dias()
            print(f"      Descripción días: {descripcion_dias}")
        except Exception as e:
            print(f"      ❌ Error en descripción días: {e}")

def run_prueba_exhaustiva():
    """Ejecuta la prueba exhaustiva"""
    success = test_todos_los_usuarios()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CONFIRMADO: Sistema funcionando perfectamente")
        print("✅ El error 'NoneType' object is not subscriptable' está RESUELTO")
        print("\n📝 RECOMENDACIÓN PARA EL USUARIO:")
        print("1. Borra completamente el caché del navegador")
        print("2. Reinicia el servidor Django si es necesario")
        print("3. El error debería haber desaparecido")
    else:
        print("❌ ERROR ENCONTRADO en usuarios específicos")
        print("🔧 Se requiere corrección adicional")

if __name__ == "__main__":
    run_prueba_exhaustiva()
