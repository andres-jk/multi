import sqlite3
import os

# Ruta a la base de datos
db_path = r"c:\Users\andre\OneDrive\Documentos\MultiAndamios\db.sqlite3"

try:
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='recibos_estadoproductoindividual';
    """)
    
    result = cursor.fetchone()
    
    if result:
        print("✓ La tabla 'recibos_estadoproductoindividual' YA EXISTE")
    else:
        print("✗ La tabla 'recibos_estadoproductoindividual' NO EXISTE - Creándola...")
        
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
    
    conn.close()
    print("\n=== ESTADO FINAL ===")
    print("La función de administración de productos individuales ahora debería funcionar correctamente.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
