#!/usr/bin/env python
"""
Script para aplicar manualmente la migración de EstadoProductoIndividual
"""
import os
import sys
import sqlite3

# Configuración básica
PROJECT_PATH = r"c:\Users\andre\OneDrive\Documentos\MultiAndamios"
DB_PATH = os.path.join(PROJECT_PATH, "db.sqlite3")

def apply_migration():
    """Aplica la migración para crear la tabla EstadoProductoIndividual"""
    
    print(f"Conectando a la base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Error: No se encontró la base de datos")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recibos_estadoproductoindividual';
        """)
        
        if cursor.fetchone():
            print("La tabla 'recibos_estadoproductoindividual' ya existe")
            return True
        
        print("Creando tabla 'recibos_estadoproductoindividual'...")
        
        # Crear la tabla
        cursor.execute("""
            CREATE TABLE "recibos_estadoproductoindividual" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "numero_serie" varchar(100),
                "estado" varchar(20) NOT NULL DEFAULT 'BUEN_ESTADO',
                "observaciones" text,
                "fecha_revision" datetime NOT NULL,
                "detalle_recibo_id" bigint NOT NULL,
                "revisado_por_id" integer,
                FOREIGN KEY ("detalle_recibo_id") REFERENCES "recibos_detallereciboobra" ("id") DEFERRABLE INITIALLY DEFERRED,
                FOREIGN KEY ("revisado_por_id") REFERENCES "usuarios_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
            );
        """)
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" 
            ON "recibos_estadoproductoindividual" ("detalle_recibo_id");
        """)
        
        cursor.execute("""
            CREATE INDEX "recibos_estadoproductoindividual_revisado_por_id_12345678" 
            ON "recibos_estadoproductoindividual" ("revisado_por_id");
        """)
        
        # Marcar la migración como aplicada
        cursor.execute("""
            INSERT OR IGNORE INTO django_migrations (app, name, applied) 
            VALUES ('recibos', '0003_estadoproductoindividual', datetime('now'));
        """)
        
        conn.commit()
        print("✓ Tabla creada exitosamente")
        print("✓ Índices creados")
        print("✓ Migración marcada como aplicada")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("=== Aplicación manual de migración ===")
    if apply_migration():
        print("✓ Migración aplicada exitosamente")
        print("La función de administración de productos individuales ahora debería funcionar.")
    else:
        print("✗ Error al aplicar la migración")
    
    input("Presiona Enter para continuar...")
