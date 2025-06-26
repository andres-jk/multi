"""
Diagnóstico rápido del problema de devolución de productos
"""
import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def diagnostico_devolucion():
    from productos.models import Producto
    from recibos.models import ReciboObra
    from django.db.models import F
    
    print("=== DIAGNÓSTICO DE DEVOLUCIÓN DE PRODUCTOS ===")
    
    # 1. Verificar productos
    print("\n1. ESTADO DE PRODUCTOS:")
    productos = Producto.objects.all()
    if productos.exists():
        for producto in productos[:3]:  # Solo los primeros 3
            total = producto.cantidad_total()
            print(f"   {producto.nombre}:")
            print(f"     - Disponible: {producto.cantidad_disponible}")
            print(f"     - En renta: {producto.cantidad_en_renta}")
            print(f"     - Reservada: {producto.cantidad_reservada}")
            print(f"     - Total: {total}")
    else:
        print("   ❌ No se encontraron productos")
    
    # 2. Verificar recibos pendientes
    print("\n2. RECIBOS CON PRODUCTOS PENDIENTES:")
    try:
        recibos_pendientes = ReciboObra.objects.filter(cantidad_vuelta__lt=F('cantidad_solicitada'))
        if recibos_pendientes.exists():
            print(f"   Se encontraron {recibos_pendientes.count()} recibos con productos pendientes:")
            for recibo in recibos_pendientes[:5]:
                pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
                print(f"     - Recibo #{recibo.id}: {pendiente} unidades de {recibo.producto.nombre}")
        else:
            print("   ✅ No hay recibos con productos pendientes")
    except Exception as e:
        print(f"   ❌ Error al consultar recibos: {e}")
    
    # 3. Verificar recibos consolidados
    print("\n3. RECIBOS CONSOLIDADOS:")
    try:
        from recibos.models import DetalleReciboObra
        detalles_pendientes = DetalleReciboObra.objects.filter(cantidad_vuelta__lt=F('cantidad_solicitada'))
        if detalles_pendientes.exists():
            print(f"   Se encontraron {detalles_pendientes.count()} detalles con productos pendientes:")
            for detalle in detalles_pendientes[:5]:
                pendiente = detalle.cantidad_solicitada - detalle.cantidad_vuelta
                print(f"     - Detalle #{detalle.id}: {pendiente} unidades de {detalle.producto.nombre}")
        else:
            print("   ✅ No hay detalles de recibos consolidados con productos pendientes")
    except Exception as e:
        print(f"   ❌ Error al consultar detalles de recibos: {e}")
    
    # 4. Probar el método de devolución
    print("\n4. PRUEBA DEL MÉTODO DE DEVOLUCIÓN:")
    try:
        producto_prueba = Producto.objects.filter(cantidad_en_renta__gt=0).first()
        if producto_prueba:
            print(f"   Probando con producto: {producto_prueba.nombre}")
            print(f"   Estado antes: En renta={producto_prueba.cantidad_en_renta}, Disponible={producto_prueba.cantidad_disponible}")
            
            # Hacer una devolución de prueba
            cantidad_test = min(1, producto_prueba.cantidad_en_renta)
            if cantidad_test > 0:
                resultado = producto_prueba.devolver_de_renta(cantidad_test)
                print(f"   Resultado de devolver {cantidad_test} unidad: {'✅ Exitoso' if resultado else '❌ Falló'}")
                
                # Verificar el estado después
                producto_prueba.refresh_from_db()
                print(f"   Estado después: En renta={producto_prueba.cantidad_en_renta}, Disponible={producto_prueba.cantidad_disponible}")
                
                # Revertir el cambio
                if resultado:
                    producto_prueba.cantidad_disponible -= cantidad_test
                    producto_prueba.cantidad_en_renta += cantidad_test
                    producto_prueba.save()
                    print(f"   Cambio revertido para mantener el estado original")
            else:
                print("   ⚠️ No hay productos en renta para probar")
        else:
            print("   ⚠️ No se encontró ningún producto con stock en renta")
    except Exception as e:
        print(f"   ❌ Error durante la prueba: {e}")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")

if __name__ == "__main__":
    diagnostico_devolucion()
