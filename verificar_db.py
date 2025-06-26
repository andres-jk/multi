"""
Verificación simple del estado de devolución
"""

# Verificar que los archivos de migración estén correctos
import sqlite3
import os

def verificar_base_datos():
    db_path = "db.sqlite3"
    
    if not os.path.exists(db_path):
        print("❌ La base de datos no existe")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar productos
        cursor.execute("SELECT COUNT(*) FROM productos_producto")
        productos_count = cursor.fetchone()[0]
        print(f"✅ Productos en DB: {productos_count}")
        
        # Verificar recibos
        cursor.execute("SELECT COUNT(*) FROM recibos_reciboobra")
        recibos_count = cursor.fetchone()[0]
        print(f"✅ Recibos en DB: {recibos_count}")
        
        # Verificar recibos pendientes
        cursor.execute("""
            SELECT COUNT(*) FROM recibos_reciboobra 
            WHERE cantidad_vuelta < cantidad_solicitada
        """)
        pendientes = cursor.fetchone()[0]
        print(f"⚠️ Recibos con productos pendientes: {pendientes}")
        
        # Verificar algunos productos específicos
        cursor.execute("""
            SELECT nombre, cantidad_disponible, cantidad_en_renta, cantidad_reservada 
            FROM productos_producto 
            WHERE cantidad_en_renta > 0 
            LIMIT 3
        """)
        productos_en_renta = cursor.fetchall()
        
        if productos_en_renta:
            print("\n📦 Productos con stock en renta:")
            for producto in productos_en_renta:
                nombre, disp, renta, res = producto
                print(f"  - {nombre}: Disponible={disp}, En renta={renta}, Reservada={res}")
        else:
            print("\n📦 No hay productos con stock en renta")
        
        # Verificar recibos específicos pendientes
        cursor.execute("""
            SELECT r.id, p.nombre, r.cantidad_solicitada, r.cantidad_vuelta,
                   (r.cantidad_solicitada - r.cantidad_vuelta) as pendiente
            FROM recibos_reciboobra r
            JOIN productos_producto p ON r.producto_id = p.id_producto
            WHERE r.cantidad_vuelta < r.cantidad_solicitada
            LIMIT 5
        """)
        recibos_pendientes = cursor.fetchall()
        
        if recibos_pendientes:
            print("\n📄 Recibos con productos pendientes:")
            for recibo in recibos_pendientes:
                rid, nombre, solicitada, vuelta, pendiente = recibo
                print(f"  - Recibo #{rid}: {pendiente} de {solicitada} unidades de {nombre} pendientes")
        
    except Exception as e:
        print(f"❌ Error consultando la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_base_datos()
