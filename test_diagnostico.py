#!/usr/bin/env python
"""
Script para probar las consultas de diagnóstico sin necesidad de autenticación web
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db.models import F, Sum
from recibos.models import ReciboObra, DetalleReciboObra
from productos.models import Producto

def test_diagnostico():
    print("=== PRUEBA DE CONSULTAS DE DIAGNÓSTICO ===")
    
    try:
        # Obtener información de productos
        productos_con_renta = Producto.objects.filter(cantidad_en_renta__gt=0)
        print(f"✅ Productos con renta: {productos_con_renta.count()}")
        
        # Obtener recibos que tienen detalles pendientes
        recibos_con_pendientes = ReciboObra.objects.filter(
            detalles__cantidad_vuelta__lt=F('detalles__cantidad_solicitada')
        ).distinct()
        print(f"✅ Recibos con pendientes: {recibos_con_pendientes.count()}")
        
        # Obtener detalles pendientes directamente
        detalles_pendientes = DetalleReciboObra.objects.filter(cantidad_vuelta__lt=F('cantidad_solicitada'))
        print(f"✅ Detalles pendientes: {detalles_pendientes.count()}")
        
        # Verificar inconsistencias
        inconsistencias = []
        
        for recibo in recibos_con_pendientes:
            for detalle in recibo.detalles.filter(cantidad_vuelta__lt=F('cantidad_solicitada')):
                pendiente = detalle.cantidad_solicitada - detalle.cantidad_vuelta
                if detalle.producto and pendiente > detalle.producto.cantidad_en_renta:
                    inconsistencias.append({
                        'detalle': detalle,
                        'pendiente': pendiente,
                        'en_renta': detalle.producto.cantidad_en_renta,
                        'producto': detalle.producto
                    })
        
        print(f"✅ Inconsistencias encontradas: {len(inconsistencias)}")
        
        # Mostrar algunos detalles
        if productos_con_renta.exists():
            print("\n--- Productos con stock en renta ---")
            for producto in productos_con_renta[:5]:
                print(f"  - {producto.nombre}: {producto.cantidad_en_renta} en renta")
        
        if recibos_con_pendientes.exists():
            print("\n--- Recibos con pendientes ---")
            for recibo in recibos_con_pendientes[:5]:
                print(f"  - Recibo #{recibo.id}: {recibo.cantidad_solicitada} solicitados, {recibo.cantidad_vuelta} devueltos")
        
        if detalles_pendientes.exists():
            print("\n--- Detalles pendientes ---")
            for detalle in detalles_pendientes[:5]:
                pendiente = detalle.cantidad_solicitada - detalle.cantidad_vuelta
                print(f"  - Detalle #{detalle.id} ({detalle.producto.nombre}): {pendiente} pendientes")
        
        print("\n✅ Todas las consultas funcionan correctamente!")
        
    except Exception as e:
        print(f"❌ Error en las consultas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_diagnostico()
