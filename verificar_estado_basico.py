#!/usr/bin/env python3
"""
Script simple para verificar el estado de MultiAndamios cuando faltan archivos
"""

import os
import sys
import subprocess

def verificar_estado_basico():
    """Verificar estado básico del sistema"""
    print("=== VERIFICACIÓN DE ESTADO BÁSICO ===")
    
    # 1. Verificar directorio actual
    print(f"Directorio actual: {os.getcwd()}")
    
    # 2. Verificar archivos críticos
    archivos_criticos = [
        'manage.py',
        'db.sqlite3',
        'multiandamios/settings.py',
        'cargar_divipola_produccion.py',
        'verificar_api_divipola.py',
        'verificacion_final_sistema.py'
    ]
    
    print("\nARCHIVOS CRÍTICOS:")
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - PRESENTE")
        else:
            print(f"❌ {archivo} - AUSENTE")
    
    # 3. Verificar estado de git
    print("\nESTADO DE GIT:")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️ Hay cambios no confirmados:")
                print(result.stdout)
            else:
                print("✅ Repositorio limpio")
        else:
            print("❌ Error al verificar git")
    except Exception as e:
        print(f"❌ Error al ejecutar git: {e}")
    
    # 4. Verificar último commit
    print("\nÚLTIMOS COMMITS:")
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Error al verificar commits")
    except Exception as e:
        print(f"❌ Error al ejecutar git log: {e}")
    
    # 5. Verificar Django
    print("\nVERIFICAR DJANGO:")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
        import django
        django.setup()
        print("✅ Django configurado correctamente")
        
        # Verificar base de datos
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            tabla_count = cursor.fetchone()[0]
            print(f"✅ Base de datos con {tabla_count} tablas")
            
    except Exception as e:
        print(f"❌ Error en Django: {e}")
    
    print("\n=== COMANDOS SUGERIDOS ===")
    print("Si faltan archivos, ejecuta:")
    print("1. git fetch --all")
    print("2. git reset --hard origin/main")
    print("3. git clean -fd")
    
    print("\nSi Django falla, ejecuta:")
    print("1. python3.10 manage.py migrate")
    print("2. python3.10 manage.py collectstatic --noinput")

if __name__ == '__main__':
    verificar_estado_basico()
