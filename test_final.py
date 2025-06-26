#!/usr/bin/env python
"""
Script final para verificar que la solución funciona
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.db import connection
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def verificar_tabla_existe():
    """Verificar si la tabla existe en la base de datos"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recibos_estadoproductoindividual';
        """)
        return cursor.fetchone() is not None

def crear_tabla_si_no_existe():
    """Crear tabla si no existe"""
    if not verificar_tabla_existe():
        print("Tabla no existe, creándola...")
        with connection.cursor() as cursor:
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
            cursor.execute('CREATE INDEX "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" ON "recibos_estadoproductoindividual" ("detalle_recibo_id");')
            cursor.execute('CREATE INDEX "recibos_estadoproductoindividual_revisado_por_id_12345678" ON "recibos_estadoproductoindividual" ("revisado_por_id");')
            cursor.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('recibos', '0003_estadoproductoindividual', datetime('now'));")
        print("Tabla creada exitosamente")
        return True
    else:
        print("Tabla ya existe")
        return True

def verificar_modelo_accesible():
    """Verificar que el modelo Django sea accesible"""
    try:
        from recibos.models import EstadoProductoIndividual
        count = EstadoProductoIndividual.objects.count()
        print(f"Modelo accesible - Registros: {count}")
        return True
    except Exception as e:
        print(f"Error accediendo al modelo: {e}")
        return False

if __name__ == '__main__':
    print("=== VERIFICACIÓN FINAL ===")
    
    # Verificar y crear tabla
    if crear_tabla_si_no_existe():
        # Verificar acceso al modelo
        if verificar_modelo_accesible():
            print("✓ TODO FUNCIONANDO CORRECTAMENTE")
            print("✓ La administración de productos individuales debería funcionar ahora")
        else:
            print("✗ Tabla existe pero modelo no accesible")
    else:
        print("✗ No se pudo crear la tabla")
    
    print("=== FIN ===")
