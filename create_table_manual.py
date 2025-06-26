import os
import sys
import django
import sqlite3

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.conf import settings

# Conectar a la base de datos SQLite
db_path = settings.DATABASES['default']['NAME']
print(f"Conectando a la base de datos: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla EstadoProductoIndividual
create_table_sql = """
CREATE TABLE IF NOT EXISTS "recibos_estadoproductoindividual" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "numero_serie" varchar(100) NULL,
    "estado" varchar(20) NOT NULL,
    "observaciones" text NULL,
    "fecha_revision" datetime NOT NULL,
    "detalle_recibo_id" bigint NOT NULL REFERENCES "recibos_detallereciboobra" ("id") DEFERRABLE INITIALLY DEFERRED,
    "revisado_por_id" integer NULL REFERENCES "usuarios_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
);
"""

try:
    cursor.execute(create_table_sql)
    print("Tabla creada exitosamente")
    
    # Crear índices
    cursor.execute('CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" ON "recibos_estadoproductoindividual" ("detalle_recibo_id");')
    cursor.execute('CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_revisado_por_id_f1234567" ON "recibos_estadoproductoindividual" ("revisado_por_id");')
    print("Índices creados exitosamente")
    
    # Marcar la migración como aplicada
    cursor.execute("""
        INSERT OR IGNORE INTO django_migrations (app, name, applied) 
        VALUES ('recibos', '0003_estadoproductoindividual', datetime('now'));
    """)
    print("Migración marcada como aplicada")
    
    conn.commit()
    print("Operación completada exitosamente")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
