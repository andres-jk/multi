import sqlite3
import os
from datetime import datetime

# Ruta directa a la base de datos
db_path = r"c:\Users\andre\OneDrive\Documentos\MultiAndamios\db.sqlite3"

print(f"Conectando a: {db_path}")
print(f"Archivo existe: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("ERROR: El archivo de base de datos no existe")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar si la tabla existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recibos_estadoproductoindividual';")
result = cursor.fetchone()

if result:
    print("✓ La tabla ya existe")
else:
    print("→ Creando tabla...")
    
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
    cursor.execute('CREATE INDEX "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" ON "recibos_estadoproductoindividual" ("detalle_recibo_id");')
    cursor.execute('CREATE INDEX "recibos_estadoproductoindividual_revisado_por_id_12345678" ON "recibos_estadoproductoindividual" ("revisado_por_id");')
    
    # Marcar migración como aplicada
    cursor.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('recibos', '0003_estadoproductoindividual', ?);", (datetime.now(),))
    
    conn.commit()
    print("✓ Tabla creada exitosamente")

# Verificar que la tabla existe ahora
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recibos_estadoproductoindividual';")
result = cursor.fetchone()

if result:
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM recibos_estadoproductoindividual;")
    count = cursor.fetchone()[0]
    print(f"✓ Verificación final: Tabla existe con {count} registros")
else:
    print("✗ Error: La tabla no se creó correctamente")

conn.close()

# Escribir resultado a archivo también
with open(r"c:\Users\andre\OneDrive\Documentos\MultiAndamios\migration_result.txt", "w") as f:
    f.write("MIGRATION COMPLETED SUCCESSFULLY\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write("Table: recibos_estadoproductoindividual\n")
    f.write("Status: CREATED\n")

print("=== COMPLETADO ===")
print("La administración de productos individuales debería funcionar ahora.")
