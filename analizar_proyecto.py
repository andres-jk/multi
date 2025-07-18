#!/usr/bin/env python3
"""
Análisis completo del proyecto MultiAndamios para identificar archivos innecesarios
"""

import os
import glob
import re
from collections import defaultdict

def analizar_proyecto():
    """Analiza el proyecto y categoriza todos los archivos"""
    
    # Directorios principales del proyecto Django
    directorios_principales = [
        'multiandamios',  # Configuración principal
        'usuarios',       # App de usuarios
        'productos',      # App de productos
        'pedidos',        # App de pedidos
        'recibos',        # App de recibos
        'chatbot',        # App de chatbot
        'templates',      # Templates globales
        'static',         # Archivos estáticos
        'media',          # Archivos multimedia
        'staticfiles',    # Archivos estáticos compilados
        'venv',           # Entorno virtual
        '.git',           # Control de versiones
        '.vscode',        # Configuración del editor
        'models',         # Modelos adicionales
    ]
    
    # Archivos esenciales del proyecto
    archivos_esenciales = [
        'manage.py',
        'requirements.txt',
        'db.sqlite3',
        '.gitignore',
        'LICENSE',
    ]
    
    # Patrones de archivos innecesarios
    patrones_innecesarios = [
        'test_*.py',
        'debug_*.py',
        'diagnostico_*.py',
        'verificar_*.py',
        'fix_*.py',
        'analizar_*.py',
        'prueba_*.py',
        'probar_*.py',
        'setup_*.py',
        'validar_*.py',
        'validacion_*.py',
        'verificacion_*.py',
        'limpieza_*.py',
        'limpiar_*.py',
        'optimizar_*.py',
        'optimizacion_*.py',
        'corregir_*.py',
        'configurar_*.py',
        'crear_*.py',
        'generar_*.py',
        'implementar_*.py',
        'iniciar_*.py',
        'migrar_*.py',
        'mostrar_*.py',
        'reparar_*.py',
        'reparacion_*.py',
        'reproductor_*.py',
        'reporte_*.py',
        'resumen_*.py',
        'resolver_*.py',
        'sync_*.py',
        'simular_*.py',
        'check_*.py',
        'clean_*.py',
        'quick_*.py',
        'final_*.py',
        'aplicar_*.py',
        'cargar_*.py',
        'estado_*.py',
        'demo_*.py',
        'instrucciones_*.py',
        'activar_*.py',
        'actualizar_*.py',
        '*.bak',
        '*.tmp',
        '*.temp',
        '*.backup',
        '*.old',
        '*.orig',
        '*.md',  # Archivos markdown de documentación
        '*.txt',  # Archivos de texto excepto requirements.txt
        '*.sh',   # Scripts de shell
        '*.html', # Archivos HTML de prueba
        '*.pdf',  # PDFs de prueba
        'SETTINGS_*.py',
        'URLS_*.py',
        'WSGI_*.py',
        'settings_*.py',
        'wsgi_*.py',
        'urls_*.py',
        'comandos_*.py',
        'script_*.py',
        'subir_*.py',
        'forzar_*.py',
    ]
    
    # Archivos a conservar específicamente
    archivos_conservar = [
        'requirements.txt',
        'README.md',
        'LICENSE',
        '.gitignore',
        'manage.py',
        'db.sqlite3',
    ]
    
    # Resultados del análisis
    resultados = {
        'archivos_esenciales': [],
        'directorios_principales': [],
        'archivos_innecesarios': [],
        'archivos_configuracion': [],
        'archivos_backup': [],
        'archivos_test': [],
        'archivos_documentacion': [],
        'archivos_scripts': [],
        'archivos_desconocidos': [],
        'total_archivos': 0,
        'total_directorios': 0,
        'tamaño_total': 0,
    }
    
    # Recorrer todos los archivos
    for root, dirs, files in os.walk('.'):
        # Filtrar directorios del entorno virtual y .git
        dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.git', '.vscode']]
        
        for file in files:
            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, '.')
            
            # Obtener tamaño del archivo
            try:
                size = os.path.getsize(filepath)
                resultados['tamaño_total'] += size
            except:
                size = 0
            
            resultados['total_archivos'] += 1
            
            # Categorizar archivo
            if file in archivos_conservar:
                resultados['archivos_esenciales'].append(relative_path)
            elif any(re.match(patron.replace('*', '.*'), file) for patron in patrones_innecesarios):
                resultados['archivos_innecesarios'].append(relative_path)
            elif file.endswith('.py') and ('SETTINGS' in file.upper() or 'URLS' in file.upper() or 'WSGI' in file.upper()):
                resultados['archivos_configuracion'].append(relative_path)
            elif file.endswith(('.bak', '.tmp', '.temp', '.backup', '.old', '.orig')):
                resultados['archivos_backup'].append(relative_path)
            elif file.startswith('test_') or file.startswith('debug_') or file.startswith('verificar_'):
                resultados['archivos_test'].append(relative_path)
            elif file.endswith('.md') or file.endswith('.txt') and file != 'requirements.txt':
                resultados['archivos_documentacion'].append(relative_path)
            elif file.endswith('.sh'):
                resultados['archivos_scripts'].append(relative_path)
            elif any(dir_name in relative_path for dir_name in directorios_principales):
                resultados['directorios_principales'].append(relative_path)
            else:
                resultados['archivos_desconocidos'].append(relative_path)
    
    # Contar directorios
    for root, dirs, files in os.walk('.'):
        resultados['total_directorios'] += len(dirs)
    
    return resultados

def mostrar_resultados(resultados):
    """Muestra los resultados del análisis"""
    
    print("🔍 ANÁLISIS COMPLETO DEL PROYECTO MULTIANDAMIOS")
    print("=" * 60)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Total de archivos: {resultados['total_archivos']}")
    print(f"   • Total de directorios: {resultados['total_directorios']}")
    print(f"   • Tamaño total: {resultados['tamaño_total'] / 1024 / 1024:.1f} MB")
    
    print(f"\n✅ ARCHIVOS ESENCIALES ({len(resultados['archivos_esenciales'])}):")
    for archivo in sorted(resultados['archivos_esenciales']):
        print(f"   • {archivo}")
    
    print(f"\n🗂️ DIRECTORIOS PRINCIPALES ({len(resultados['directorios_principales'])}):")
    directorios = set()
    for archivo in resultados['directorios_principales']:
        dir_name = archivo.split('/')[0] if '/' in archivo else archivo.split('\\')[0]
        directorios.add(dir_name)
    for directorio in sorted(directorios):
        print(f"   • {directorio}/")
    
    print(f"\n❌ ARCHIVOS INNECESARIOS ({len(resultados['archivos_innecesarios'])}):")
    for archivo in sorted(resultados['archivos_innecesarios'])[:20]:  # Mostrar solo los primeros 20
        print(f"   • {archivo}")
    if len(resultados['archivos_innecesarios']) > 20:
        print(f"   ... y {len(resultados['archivos_innecesarios']) - 20} más")
    
    print(f"\n⚙️ ARCHIVOS DE CONFIGURACIÓN ({len(resultados['archivos_configuracion'])}):")
    for archivo in sorted(resultados['archivos_configuracion']):
        print(f"   • {archivo}")
    
    print(f"\n🔒 ARCHIVOS DE BACKUP ({len(resultados['archivos_backup'])}):")
    for archivo in sorted(resultados['archivos_backup']):
        print(f"   • {archivo}")
    
    print(f"\n🧪 ARCHIVOS DE TEST/DEBUG ({len(resultados['archivos_test'])}):")
    for archivo in sorted(resultados['archivos_test'])[:10]:  # Mostrar solo los primeros 10
        print(f"   • {archivo}")
    if len(resultados['archivos_test']) > 10:
        print(f"   ... y {len(resultados['archivos_test']) - 10} más")
    
    print(f"\n📚 ARCHIVOS DE DOCUMENTACIÓN ({len(resultados['archivos_documentacion'])}):")
    for archivo in sorted(resultados['archivos_documentacion'])[:10]:  # Mostrar solo los primeros 10
        print(f"   • {archivo}")
    if len(resultados['archivos_documentacion']) > 10:
        print(f"   ... y {len(resultados['archivos_documentacion']) - 10} más")
    
    print(f"\n📜 SCRIPTS DE SHELL ({len(resultados['archivos_scripts'])}):")
    for archivo in sorted(resultados['archivos_scripts']):
        print(f"   • {archivo}")
    
    print(f"\n❓ ARCHIVOS DESCONOCIDOS ({len(resultados['archivos_desconocidos'])}):")
    for archivo in sorted(resultados['archivos_desconocidos'])[:10]:  # Mostrar solo los primeros 10
        print(f"   • {archivo}")
    if len(resultados['archivos_desconocidos']) > 10:
        print(f"   ... y {len(resultados['archivos_desconocidos']) - 10} más")
    
    # Resumen de limpieza
    total_innecesarios = (
        len(resultados['archivos_innecesarios']) +
        len(resultados['archivos_configuracion']) +
        len(resultados['archivos_backup']) +
        len(resultados['archivos_test']) +
        len(resultados['archivos_documentacion']) +
        len(resultados['archivos_scripts'])
    )
    
    print(f"\n🧹 RESUMEN DE LIMPIEZA:")
    print(f"   • Total archivos innecesarios: {total_innecesarios}")
    print(f"   • Archivos a conservar: {len(resultados['archivos_esenciales']) + len(resultados['directorios_principales'])}")
    print(f"   • Porcentaje de limpieza: {(total_innecesarios / resultados['total_archivos']) * 100:.1f}%")

def generar_reporte():
    """Genera un reporte detallado del análisis"""
    
    print("\n🔍 ANALIZANDO PROYECTO MULTIANDAMIOS...")
    print("Por favor espera mientras se analizan todos los archivos...")
    
    resultados = analizar_proyecto()
    mostrar_resultados(resultados)
    
    print(f"\n✅ ANÁLISIS COMPLETADO")
    print("=" * 60)
    
    return resultados

if __name__ == "__main__":
    generar_reporte()
