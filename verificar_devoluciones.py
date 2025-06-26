"""
Script directo para verificar problemas de devolución usando sqlite3
"""
import sqlite3
import os
from datetime import datetime

def verificar_estado_devoluciones():
    print("=== VERIFICACIÓN DIRECTA DE DEVOLUCIONES ===")
    
    # Verificar que existe la base de datos
    if not os.path.exists('db.sqlite3'):
        print("❌ No se encontró la base de datos db.sqlite3")
        return
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # 1. Estado general de productos
        print("\n1. PRODUCTOS CON STOCK EN RENTA:")
        cursor.execute("""
            SELECT nombre, cantidad_disponible, cantidad_en_renta, cantidad_reservada,
                   (cantidad_disponible + cantidad_en_renta + cantidad_reservada) as total
            FROM productos_producto 
            WHERE cantidad_en_renta > 0
            ORDER BY cantidad_en_renta DESC
        """)
        
        productos_en_renta = cursor.fetchall()
        if productos_en_renta:
            for producto in productos_en_renta:
                nombre, disp, renta, res, total = producto
                print(f"   • {nombre}: Disponible={disp}, En renta={renta}, Reservada={res}, Total={total}")
        else:
            print("   ✅ No hay productos con stock en renta")
        
        # 2. Recibos simples pendientes
        print("\n2. RECIBOS SIMPLES PENDIENTES:")
        cursor.execute("""
            SELECT r.id, p.nombre, r.cantidad_solicitada, r.cantidad_vuelta,
                   (r.cantidad_solicitada - r.cantidad_vuelta) as pendiente,
                   r.fecha_entrega, r.estado
            FROM recibos_reciboobra r
            JOIN productos_producto p ON r.producto_id = p.id_producto
            WHERE r.cantidad_vuelta < r.cantidad_solicitada
            ORDER BY r.fecha_entrega DESC
        """)
        
        recibos_pendientes = cursor.fetchall()
        if recibos_pendientes:
            print(f"   Se encontraron {len(recibos_pendientes)} recibos con productos pendientes:")
            for recibo in recibos_pendientes:
                rid, nombre, solicitada, vuelta, pendiente, fecha, estado = recibo
                print(f"   • Recibo #{rid}: {pendiente} de {solicitada} unidades de '{nombre}' pendientes")
                print(f"     Fecha: {fecha}, Estado: {estado}")
        else:
            print("   ✅ No hay recibos simples con productos pendientes")
        
        # 3. Verificar inconsistencias entre recibos y inventario
        print("\n3. INCONSISTENCIAS DE INVENTARIO:")
        cursor.execute("""
            SELECT r.id, p.nombre, 
                   (r.cantidad_solicitada - r.cantidad_vuelta) as pendiente,
                   p.cantidad_en_renta,
                   CASE 
                       WHEN (r.cantidad_solicitada - r.cantidad_vuelta) > p.cantidad_en_renta 
                       THEN 'INCONSISTENTE'
                       ELSE 'OK'
                   END as estado_consistencia
            FROM recibos_reciboobra r
            JOIN productos_producto p ON r.producto_id = p.id_producto
            WHERE r.cantidad_vuelta < r.cantidad_solicitada
            AND (r.cantidad_solicitada - r.cantidad_vuelta) > p.cantidad_en_renta
        """)
        
        inconsistencias = cursor.fetchall()
        if inconsistencias:
            print(f"   ⚠️ Se encontraron {len(inconsistencias)} inconsistencias:")
            for inc in inconsistencias:
                rid, nombre, pendiente, en_renta, estado = inc
                print(f"   • Recibo #{rid}: Necesita {pendiente} de '{nombre}' pero solo hay {en_renta} en renta")
        else:
            print("   ✅ No hay inconsistencias entre recibos y inventario")
        
        # 4. Recibos consolidados (si existen)
        print("\n4. RECIBOS CONSOLIDADOS:")
        cursor.execute("""
            SELECT COUNT(*) FROM recibos_detallereciboobra
        """)
        
        count_detalles = cursor.fetchone()[0]
        if count_detalles > 0:
            print(f"   Se encontraron {count_detalles} detalles de recibos consolidados")
            
            cursor.execute("""
                SELECT d.id, d.recibo_id, p.nombre, d.cantidad_solicitada, d.cantidad_vuelta,
                       (d.cantidad_solicitada - d.cantidad_vuelta) as pendiente
                FROM recibos_detallereciboobra d
                JOIN productos_producto p ON d.producto_id = p.id_producto
                WHERE d.cantidad_vuelta < d.cantidad_solicitada
            """)
            
            detalles_pendientes = cursor.fetchall()
            if detalles_pendientes:
                print(f"   ⚠️ {len(detalles_pendientes)} detalles con productos pendientes:")
                for detalle in detalles_pendientes:
                    did, rid, nombre, solicitada, vuelta, pendiente = detalle
                    print(f"   • Detalle #{did} (Recibo #{rid}): {pendiente} de {solicitada} '{nombre}' pendientes")
            else:
                print("   ✅ No hay detalles consolidados con productos pendientes")
        else:
            print("   ℹ️ No hay recibos consolidados en el sistema")
        
        # 5. Resumen final
        print("\n5. RESUMEN:")
        total_problemas = len(recibos_pendientes) + len(inconsistencias)
        if count_detalles > 0:
            cursor.execute("""
                SELECT COUNT(*) FROM recibos_detallereciboobra 
                WHERE cantidad_vuelta < cantidad_solicitada
            """)
            detalles_problemas = cursor.fetchone()[0]
            total_problemas += detalles_problemas
        
        if total_problemas > 0:
            print(f"   ⚠️ TOTAL DE PROBLEMAS ENCONTRADOS: {total_problemas}")
            print("   💡 Los productos no se están devolviendo correctamente al inventario")
            print("   🔧 Se recomienda:")
            print("      1. Verificar que las funciones de devolución estén siendo llamadas")
            print("      2. Revisar los logs de aplicación para errores")
            print("      3. Usar el panel de administración para procesar devoluciones manualmente")
        else:
            print("   ✅ El sistema de devoluciones está funcionando correctamente")
    
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
    
    finally:
        conn.close()
    
    print("\n=== FIN DE LA VERIFICACIÓN ===")

if __name__ == "__main__":
    verificar_estado_devoluciones()
