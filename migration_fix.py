"""
Migración manual para corregir el modelo ReciboObra
"""
import sqlite3
import os

def agregar_campos_recibo():
    """Agregar campos faltantes al modelo ReciboObra"""
    if not os.path.exists('db.sqlite3'):
        print("❌ La base de datos no existe")
        return False
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(recibos_reciboobra)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Columnas existentes: {columns}")
        
        # Campos que necesitamos agregar
        nuevos_campos = [
            ('producto_id', 'INTEGER'),
            ('cantidad_solicitada', 'INTEGER'),
            ('cantidad_vuelta', 'INTEGER DEFAULT 0'),
            ('cantidad_buen_estado', 'INTEGER DEFAULT 0'),
            ('cantidad_danados', 'INTEGER DEFAULT 0'),
            ('cantidad_inservibles', 'INTEGER DEFAULT 0'),
            ('estado', 'VARCHAR(50) DEFAULT "PENDIENTE"'),
        ]
        
        for campo, tipo in nuevos_campos:
            if campo not in columns:
                cursor.execute(f'ALTER TABLE recibos_reciboobra ADD COLUMN {campo} {tipo}')
                print(f"✅ Campo '{campo}' agregado")
        
        conn.commit()
        print("✅ Migración completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    agregar_campos_recibo()
