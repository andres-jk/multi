"""
Script para verificar que la devolución de productos al inventario funcione correctamente.
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')

import django
django.setup()

from productos.models import Producto
from recibos.models import ReciboObra, DetalleReciboObra
from pedidos.models import Pedido, DetallePedido
from usuarios.models import Usuario, Cliente
from django.utils import timezone
from django.db import models

def test_devolucion_flujo():
    """Prueba el flujo completo de devolución de productos"""
    print("=== PRUEBA DE DEVOLUCIÓN DE PRODUCTOS ===")
    
    # Verificar que existe al menos un producto
    producto = Producto.objects.first()
    if not producto:
        print("No hay productos en la base de datos. Creando uno para prueba...")
        producto = Producto.objects.create(
            nombre="Andamio de Prueba",
            descripcion="Producto para pruebas de devolución",
            precio=100.00,
            tipo_renta="DIARIO",
            cantidad_disponible=10,
            cantidad_reservada=0,
            cantidad_en_renta=5,  # Simular que hay 5 en renta
            activo=True
        )
    
    print(f"Producto para prueba: {producto.nombre}")
    print(f"Estado inicial del inventario:")
    print(f"  - Disponible: {producto.cantidad_disponible}")
    print(f"  - Reservada: {producto.cantidad_reservada}")
    print(f"  - En renta: {producto.cantidad_en_renta}")
    print(f"  - Total: {producto.cantidad_total()}")
    
    # Prueba 1: Devolución normal usando el método correcto
    print("\n--- Prueba 1: Devolución normal ---")
    cantidad_a_devolver = 2
    
    if producto.cantidad_en_renta >= cantidad_a_devolver:
        disponible_antes = producto.cantidad_disponible
        en_renta_antes = producto.cantidad_en_renta
        
        # Usar el método correcto para devolver
        resultado = producto.devolver_de_renta(cantidad_a_devolver)
        
        if resultado:
            # Refrescar el producto para ver los cambios
            producto.refresh_from_db()
            print(f"✅ Devolución exitosa de {cantidad_a_devolver} unidades")
            print(f"  - Disponible: {disponible_antes} → {producto.cantidad_disponible}")
            print(f"  - En renta: {en_renta_antes} → {producto.cantidad_en_renta}")
        else:
            print(f"❌ Error en la devolución")
    else:
        print(f"❌ No hay suficientes productos en renta ({producto.cantidad_en_renta} < {cantidad_a_devolver})")
    
    # Prueba 2: Intentar devolver más de lo que hay en renta
    print("\n--- Prueba 2: Intentar devolver más de lo disponible ---")
    cantidad_excesiva = producto.cantidad_en_renta + 5
    
    resultado = producto.devolver_de_renta(cantidad_excesiva)
    if not resultado:
        print(f"✅ El sistema correctamente rechazó devolver {cantidad_excesiva} unidades (solo hay {producto.cantidad_en_renta} en renta)")
    else:
        print(f"❌ ERROR: El sistema permitió una devolución inválida")
    
    # Verificar que el estado del producto no cambió después del intento fallido
    producto.refresh_from_db()
    print(f"Estado después del intento fallido:")
    print(f"  - Disponible: {producto.cantidad_disponible}")
    print(f"  - En renta: {producto.cantidad_en_renta}")
    
    print("\n=== FIN DE PRUEBAS ===")

def verificar_recibos_pendientes():
    """Verifica si hay recibos con productos pendientes de devolución"""
    print("\n=== VERIFICACIÓN DE RECIBOS PENDIENTES ===")
    
    recibos_pendientes = ReciboObra.objects.filter(cantidad_vuelta__lt=models.F('cantidad_solicitada'))
    
    if recibos_pendientes.exists():
        print(f"Se encontraron {recibos_pendientes.count()} recibos con productos pendientes de devolución:")
        for recibo in recibos_pendientes[:5]:  # Mostrar solo los primeros 5
            pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
            print(f"  - Recibo #{recibo.id}: {pendiente} unidades de {recibo.producto.nombre} pendientes")
    else:
        print("✅ No hay recibos con productos pendientes de devolución")
    
    # Verificar recibos consolidados
    from django.db.models import F
    recibos_consolidados = ReciboObra.objects.filter(detalles__isnull=False).distinct()
    
    if recibos_consolidados.exists():
        print(f"\nSe encontraron {recibos_consolidados.count()} recibos consolidados:")
        for recibo in recibos_consolidados[:3]:
            print(f"  - Recibo consolidado #{recibo.id} con {recibo.detalles.count()} productos")
            for detalle in recibo.detalles.all():
                if detalle.cantidad_pendiente > 0:
                    print(f"    * {detalle.producto.nombre}: {detalle.cantidad_pendiente} pendientes")

if __name__ == "__main__":
    try:
        test_devolucion_flujo()
        verificar_recibos_pendientes()
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
