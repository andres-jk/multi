#!/usr/bin/env python
"""
Script para verificar y crear la tabla EstadoProductoIndividual usando Django shell
"""
import os
import sys

# Agregar el proyecto al path de Python
sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')

import django
django.setup()

# Importar los modelos
from recibos.models import EstadoProductoIndividual
from django.db import connection

def test_table():
    """Verificar que la tabla funciona correctamente"""
    try:
        # Intentar contar registros
        count = EstadoProductoIndividual.objects.count()
        print(f"SUCCESS: Tabla accesible, registros: {count}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def create_table_with_sql():
    """Crear la tabla usando SQL directo si no existe"""
    with connection.cursor() as cursor:
        try:
            # Intentar crear la tabla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS "recibos_estadoproductoindividual" (
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
            cursor.execute('CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" ON "recibos_estadoproductoindividual" ("detalle_recibo_id");')
            cursor.execute('CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_revisado_por_id_12345678" ON "recibos_estadoproductoindividual" ("revisado_por_id");')
            
            # Marcar migración como aplicada
            cursor.execute("""
                INSERT OR IGNORE INTO django_migrations (app, name, applied) 
                VALUES ('recibos', '0003_estadoproductoindividual', datetime('now'));
            """)
            
            print("SUCCESS: Tabla creada con SQL directo")
            return True
            
        except Exception as e:
            print(f"ERROR creando tabla: {e}")
            return False

if __name__ == '__main__':
    print("=== VERIFICACIÓN DE TABLA ===")
    
    # Primero intentar acceder a la tabla
    if test_table():
        print("✓ La tabla ya funciona correctamente")
    else:
        print("→ Intentando crear la tabla...")
        if create_table_with_sql():
            # Verificar nuevamente
            if test_table():
                print("✓ Tabla creada y funcionando")
            else:
                print("✗ Error: Tabla creada pero no accesible")
        else:
            print("✗ Error: No se pudo crear la tabla")
    
    print("=== FIN ===")
