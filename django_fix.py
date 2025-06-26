#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection

def fix_database():
    """Crea la tabla faltante usando Django connection"""
    with connection.cursor() as cursor:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recibos_estadoproductoindividual';
        """)
        
        table_exists = cursor.fetchone()
        
        with open('migration_result.txt', 'w') as f:
            if table_exists:
                f.write("ESTADO: La tabla 'recibos_estadoproductoindividual' YA EXISTE\n")
            else:
                f.write("ESTADO: Creando tabla 'recibos_estadoproductoindividual'...\n")
                
                try:
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
                    
                    f.write("EXITO: Tabla creada exitosamente\n")
                    f.write("EXITO: Indices creados\n")
                    f.write("EXITO: Migracion marcada como aplicada\n")
                    
                    # Verificar que podemos usar el modelo
                    from recibos.models import EstadoProductoIndividual
                    count = EstadoProductoIndividual.objects.count()
                    f.write(f"VERIFICACION: Modelo accesible, registros: {count}\n")
                    
                except Exception as e:
                    f.write(f"ERROR: {str(e)}\n")
                    import traceback
                    f.write(f"TRACEBACK: {traceback.format_exc()}\n")

if __name__ == '__main__':
    fix_database()
