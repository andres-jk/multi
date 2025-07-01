#!/usr/bin/env python
"""
Script para simular exactamente la vista detalle_mi_pedido
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from pedidos.models import Pedido
from usuarios.models import Cliente, Usuario

def simular_vista_detalle():
    """Simular exactamente lo que hace la vista detalle_mi_pedido"""
    print("=== SIMULACIÓN DE VISTA DETALLE_MI_PEDIDO ===\n")
    
    # Obtener usuario y cliente como en la vista real
    try:
        usuario = Usuario.objects.get(username='oscar_ibañez')
        cliente = Cliente.objects.get(usuario=usuario)
        print(f"✅ Usuario: {usuario.username}")
        print(f"✅ Cliente: {cliente}")
        
        # Obtener pedido #30 como en la vista real
        pedido = get_object_or_404(Pedido, id_pedido=30, cliente=cliente)
        print(f"✅ Pedido: #{pedido.id_pedido}")
        
        # Crear contexto exacto como en la vista
        context = {
            'pedido': pedido,
            'detalles': pedido.detalles.all().select_related('producto'),
            'cliente': cliente,
        }
        
        print(f"📝 Detalles en contexto: {context['detalles'].count()}")
        for detalle in context['detalles']:
            print(f"    - {detalle.producto.nombre}: {detalle.cantidad} x {detalle.dias_renta} días = ${detalle.subtotal}")
        
        # Intentar renderizar el template real
        try:
            html = render_to_string('pedidos/detalle_mi_pedido.html', context)
            
            # Guardar para inspección
            with open(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios\debug_vista_real.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            print("✅ Template real renderizado exitosamente")
            print("📄 Guardado como debug_vista_real.html")
            
            # Análisis básico del contenido
            if f"Pedido #{pedido.id_pedido}" in html:
                print("✅ Número de pedido presente")
            else:
                print("❌ Número de pedido NO presente")
            
            if "andamio certificado" in html.lower():
                print("✅ Nombre del producto presente")
            else:
                print("❌ Nombre del producto NO presente")
            
            # Buscar la tabla específicamente
            if "<table" in html:
                print("✅ Elemento table encontrado")
                
                # Contar filas de datos
                import re
                rows = re.findall(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
                print(f"📊 Filas de tabla encontradas: {len(rows)}")
                
                # Buscar datos específicos en las filas
                for i, row in enumerate(rows):
                    if "andamio" in row.lower():
                        print(f"✅ Fila {i} contiene producto")
                        break
                else:
                    print("❌ Ninguna fila contiene el producto")
            else:
                print("❌ Elemento table NO encontrado")
            
            # Verificar si hay errores de template
            if "error" in html.lower() or "exception" in html.lower():
                print("⚠️  Posibles errores en el template")
            
        except Exception as e:
            print(f"❌ Error al renderizar template real: {e}")
            import traceback
            traceback.print_exc()
            
    except Usuario.DoesNotExist:
        print("❌ Usuario no encontrado")
    except Cliente.DoesNotExist:
        print("❌ Cliente no encontrado")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    simular_vista_detalle()
