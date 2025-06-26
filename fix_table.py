import os
import django
import sqlite3

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection

def create_missing_table():
    """Crea la tabla EstadoProductoIndividual si no existe"""
    
    # SQL para crear la tabla
    sql_create = """
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
    """
    
    # SQL para crear índices
    sql_indexes = [
        'CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" ON "recibos_estadoproductoindividual" ("detalle_recibo_id");',
        'CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_revisado_por_id_12345678" ON "recibos_estadoproductoindividual" ("revisado_por_id");'
    ]
    
    with connection.cursor() as cursor:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recibos_estadoproductoindividual';
        """)
        
        if not cursor.fetchone():
            print("Creando tabla recibos_estadoproductoindividual...")
            cursor.execute(sql_create)
            
            for index_sql in sql_indexes:
                cursor.execute(index_sql)
            
            # Marcar migración como aplicada
            cursor.execute("""
                INSERT OR IGNORE INTO django_migrations (app, name, applied) 
                VALUES ('recibos', '0003_estadoproductoindividual', datetime('now'));
            """)
            
            print("Tabla creada exitosamente")
        else:
            print("La tabla ya existe")

if __name__ == '__main__':
    try:
        create_missing_table()
        print("Operación completada")
        
        # Verificar que podemos importar el modelo
        from recibos.models import EstadoProductoIndividual
        count = EstadoProductoIndividual.objects.count()
        print(f"Modelo accesible. Registros: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
