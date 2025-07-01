#!/usr/bin/env python
"""
Prueba final del sistema con el producto correcto
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from productos.models import Producto
from usuarios.models import CarritoItem, Usuario

def main():
    print("=== PRUEBA FINAL ===\n")
    
    # Obtener el andamio certificado (8600 pesos, 7 días mínimo)
    producto = Producto.objects.get(nombre__icontains="andamio certificado")
    usuario = Usuario.objects.first()
    
    print(f"Producto: {producto.nombre}")
    print(f"Precio diario: ${producto.precio_diario}")
    print(f"Días mínimos: {producto.dias_minimos_renta}")
    
    # Crear item de carrito
    CarritoItem.objects.filter(usuario=usuario).delete()
    
    item = CarritoItem.objects.create(
        usuario=usuario,
        producto=producto,
        cantidad=5,
        dias_renta=7
    )
    
    print(f"\nItem creado:")
    print(f"- Cantidad: {item.cantidad}")
    print(f"- Días: {item.dias_renta}")
    print(f"- Subtotal: ${item.subtotal}")
    
    # Verificación del cálculo
    esperado = 8600 * 7 * 5  # 301,000
    print(f"\nVerificación:")
    print(f"- Cálculo esperado: 8,600 × 7 × 5 = ${esperado:,}")
    print(f"- Cálculo obtenido: ${item.subtotal}")
    
    if float(item.subtotal) == esperado:
        print("✅ CÁLCULO CORRECTO")
    else:
        print("❌ ERROR EN CÁLCULO")
    
    # Verificar que el error anterior era porque 8600 × 7 × 1 = 60,200
    precio_una_unidad = 8600 * 7 * 1
    print(f"\nPara 1 unidad por 7 días:")
    print(f"- Esperado: 8,600 × 7 × 1 = ${precio_una_unidad:,}")
    
    item_una_unidad = CarritoItem.objects.create(
        usuario=usuario,
        producto=producto,
        cantidad=1,
        dias_renta=7
    )
    print(f"- Obtenido: ${item_una_unidad.subtotal}")
    
    if float(item_una_unidad.subtotal) == precio_una_unidad:
        print("✅ CÁLCULO PARA 1 UNIDAD CORRECTO")
    else:
        print("❌ ERROR EN CÁLCULO PARA 1 UNIDAD")

if __name__ == '__main__':
    main()
