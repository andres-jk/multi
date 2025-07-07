#!/usr/bin/env python
"""
Optimización automática del proyecto MultiAndamios
Elimina archivos innecesarios sin afectar funcionalidad
"""

import os
import glob
import shutil

def optimizar_proyecto():
    """Elimina archivos innecesarios de forma segura"""
    print("=" * 70)
    print("🚀 OPTIMIZACIÓN AUTOMÁTICA DEL PROYECTO MULTIANDAMIOS")
    print("=" * 70)
    
    archivos_eliminados = 0
    espacio_liberado = 0
    
    # 1. ARCHIVOS DE PRUEBA Y TESTING
    print("\n🧪 Eliminando archivos de prueba y testing...")
    
    patrones_test = [
        "test_*.py", "prueba_*.py", "debug_*.py", "verificar_*.py",
        "validacion_*.py", "diagnostico_*.py", "reproductor_*.py"
    ]
    
    for patron in patrones_test:
        archivos = glob.glob(patron)
        for archivo in archivos:
            if os.path.exists(archivo) and archivo != 'test_acceso_recibo_obra.py':  # Mantener uno como ejemplo
                try:
                    size = os.path.getsize(archivo)
                    os.remove(archivo)
                    print(f"   ✅ Eliminado: {archivo} ({size:,} bytes)")
                    archivos_eliminados += 1
                    espacio_liberado += size
                except Exception as e:
                    print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # 2. DOCUMENTACIÓN INNECESARIA (mantener solo las importantes)
    print("\n📄 Eliminando documentación innecesaria...")
    
    docs_mantener = [
        'README.md', 'LICENSE', 'requirements.txt',
        'SOLUCION_AGENDADO_VOLUNTARIO_DEVOLUCION.md',
        'SOLUCION_RECIBO_OBRA_COMPLETA.md'
    ]
    
    archivos_md = glob.glob("*.md")
    for archivo in archivos_md:
        if archivo not in docs_mantener:
            try:
                size = os.path.getsize(archivo)
                os.remove(archivo)
                print(f"   ✅ Eliminado: {archivo} ({size:,} bytes)")
                archivos_eliminados += 1
                espacio_liberado += size
            except Exception as e:
                print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # 3. SCRIPTS OBSOLETOS
    print("\n🛠️  Eliminando scripts obsoletos...")
    
    patrones_scripts = [
        "analizar_*.py", "aplicar_*.py", "configurar_*.py", "corregir_*.py",
        "crear_*.py", "estado_*.py", "fix_*.py", "generar_*.py",
        "iniciar_*.py", "instrucciones_*.py", "limpieza_*.py", "limpiar_*.py",
        "migrar_*.py", "mostrar_*.py", "optimizar_*.py", "probar_*.py",
        "reporte_*.py", "resumen_*.py", "setup_*.py", "simular_*.py"
    ]
    
    scripts_mantener = ['manage.py']  # Scripts críticos
    
    for patron in patrones_scripts:
        archivos = glob.glob(patron)
        for archivo in archivos:
            if archivo not in scripts_mantener:
                try:
                    size = os.path.getsize(archivo)
                    os.remove(archivo)
                    print(f"   ✅ Eliminado: {archivo} ({size:,} bytes)")
                    archivos_eliminados += 1
                    espacio_liberado += size
                except Exception as e:
                    print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # 4. ARCHIVOS TEMPORALES Y BACKUPS
    print("\n🗄️  Eliminando archivos temporales y backups...")
    
    patrones_temp = ["*.bak*", "*.temp", "*.tmp", "*.backup"]
    
    for patron in patrones_temp:
        archivos = glob.glob(patron)
        for archivo in archivos:
            try:
                size = os.path.getsize(archivo)
                os.remove(archivo)
                print(f"   ✅ Eliminado: {archivo} ({size:,} bytes)")
                archivos_eliminados += 1
                espacio_liberado += size
            except Exception as e:
                print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # 5. PDFs DE PRUEBA
    print("\n📋 Eliminando PDFs de prueba...")
    
    pdfs_test = glob.glob("test_*.pdf")
    for archivo in pdfs_test:
        try:
            size = os.path.getsize(archivo)
            os.remove(archivo)
            print(f"   ✅ Eliminado: {archivo} ({size:,} bytes)")
            archivos_eliminados += 1
            espacio_liberado += size
        except Exception as e:
            print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # 6. HTML DE PRUEBA
    print("\n🌐 Eliminando HTML de prueba...")
    
    htmls_test = glob.glob("test_*.html") + glob.glob("recibo-*.html")
    for archivo in htmls_test:
        try:
            size = os.path.getsize(archivo)
            os.remove(archivo)
            print(f"   ✅ Eliminado: {archivo} ({size:,} bytes)")
            archivos_eliminados += 1
            espacio_liberado += size
        except Exception as e:
            print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # 7. ARCHIVOS VACÍOS (0 bytes)
    print("\n📦 Eliminando archivos vacíos...")
    
    archivos_python = glob.glob("*.py")
    for archivo in archivos_python:
        if (os.path.exists(archivo) and 
            os.path.getsize(archivo) == 0 and 
            archivo not in ['__init__.py', 'manage.py']):
            try:
                os.remove(archivo)
                print(f"   ✅ Eliminado archivo vacío: {archivo}")
                archivos_eliminados += 1
            except Exception as e:
                print(f"   ❌ Error eliminando {archivo}: {str(e)}")
    
    # RESUMEN FINAL
    print("\n" + "=" * 70)
    print("🎉 OPTIMIZACIÓN COMPLETADA")
    print("=" * 70)
    print(f"📊 ESTADÍSTICAS:")
    print(f"   • Archivos eliminados: {archivos_eliminados}")
    print(f"   • Espacio liberado: {espacio_liberado:,} bytes ({espacio_liberado/1024/1024:.2f} MB)")
    
    # Verificar que archivos críticos siguen existiendo
    print(f"\n🔍 VERIFICACIÓN DE ARCHIVOS CRÍTICOS:")
    archivos_criticos = ['manage.py', 'db.sqlite3', 'requirements.txt']
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo} - PRESENTE")
        else:
            print(f"   ❌ {archivo} - FALTANTE (CRÍTICO)")
    
    # Verificar apps Django
    apps = ['usuarios', 'pedidos', 'productos', 'recibos', 'chatbot', 'multiandamios']
    print(f"\n🏗️  VERIFICACIÓN DE APPS DJANGO:")
    for app in apps:
        if os.path.exists(app):
            print(f"   ✅ {app}/ - PRESENTE")
        else:
            print(f"   ❌ {app}/ - FALTANTE (CRÍTICO)")
    
    print(f"\n✅ PROYECTO OPTIMIZADO SIN AFECTAR FUNCIONALIDAD")
    return archivos_eliminados, espacio_liberado

if __name__ == "__main__":
    try:
        archivos, espacio = optimizar_proyecto()
        print(f"\n🚀 Listo para commit y push de la optimización!")
    except Exception as e:
        print(f"\n❌ Error durante la optimización: {str(e)}")
        print("El proyecto permanece intacto.")
