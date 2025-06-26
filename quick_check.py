import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Verificar columnas existentes
cursor.execute("PRAGMA table_info(recibos_reciboobra)")
columns = [col[1] for col in cursor.fetchall()]
print("Columnas existentes:", columns)

# Agregar columnas faltantes
nuevas_columnas = [
    "producto_id INTEGER",
    "cantidad_solicitada INTEGER", 
    "cantidad_vuelta INTEGER DEFAULT 0",
    "cantidad_buen_estado INTEGER DEFAULT 0",
    "cantidad_danados INTEGER DEFAULT 0", 
    "cantidad_inservibles INTEGER DEFAULT 0",
    "estado VARCHAR(50) DEFAULT 'PENDIENTE'"
]

for columna in nuevas_columnas:
    nombre_columna = columna.split()[0]
    if nombre_columna not in columns:
        try:
            cursor.execute(f"ALTER TABLE recibos_reciboobra ADD COLUMN {columna}")
            print(f"✓ Agregada columna: {nombre_columna}")
        except Exception as e:
            print(f"✗ Error agregando {nombre_columna}: {e}")

conn.commit()
conn.close()
print("Migración completada")
