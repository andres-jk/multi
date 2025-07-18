#!/usr/bin/env python3
"""
Análisis simple del proyecto MultiAndamios
"""

import os
import glob

def main():
    print("🔍 ANÁLISIS DEL PROYECTO MULTIANDAMIOS")
    print("=" * 50)
    
    # Archivos de prueba/test
    test_files = glob.glob("test_*.py")
    debug_files = glob.glob("debug_*.py")
    verificar_files = glob.glob("verificar_*.py")
    
    print(f"\n📊 ARCHIVOS DE PRUEBA Y DEBUG:")
    print(f"   • Archivos test_*.py: {len(test_files)}")
    print(f"   • Archivos debug_*.py: {len(debug_files)}")
    print(f"   • Archivos verificar_*.py: {len(verificar_files)}")
    
    # Archivos de configuración duplicados
    settings_files = glob.glob("SETTINGS_*.py")
    urls_files = glob.glob("URLS_*.py")
    wsgi_files = glob.glob("WSGI_*.py")
    
    print(f"\n⚙️ ARCHIVOS DE CONFIGURACIÓN DUPLICADOS:")
    print(f"   • Archivos SETTINGS_*.py: {len(settings_files)}")
    print(f"   • Archivos URLS_*.py: {len(urls_files)}")
    print(f"   • Archivos WSGI_*.py: {len(wsgi_files)}")
    
    # Archivos de documentación
    md_files = glob.glob("*.md")
    txt_files = [f for f in glob.glob("*.txt") if f != "requirements.txt"]
    
    print(f"\n📚 ARCHIVOS DE DOCUMENTACIÓN:")
    print(f"   • Archivos *.md: {len(md_files)}")
    print(f"   • Archivos *.txt (excepto requirements.txt): {len(txt_files)}")
    
    # Scripts de shell
    sh_files = glob.glob("*.sh")
    
    print(f"\n📜 SCRIPTS DE SHELL:")
    print(f"   • Archivos *.sh: {len(sh_files)}")
    
    # Archivos temporales y de limpieza
    fix_files = glob.glob("fix_*.py")
    limpiar_files = glob.glob("limpiar_*.py")
    
    print(f"\n🧹 ARCHIVOS DE LIMPIEZA Y CORRECCIÓN:")
    print(f"   • Archivos fix_*.py: {len(fix_files)}")
    print(f"   • Archivos limpiar_*.py: {len(limpiar_files)}")
    
    # Total de archivos innecesarios
    total_innecesarios = (len(test_files) + len(debug_files) + len(verificar_files) + 
                         len(settings_files) + len(urls_files) + len(wsgi_files) + 
                         len(md_files) + len(txt_files) + len(sh_files) + 
                         len(fix_files) + len(limpiar_files))
    
    print(f"\n🗑️ TOTAL DE ARCHIVOS INNECESARIOS: {total_innecesarios}")
    
    # Archivos esenciales del proyecto
    print(f"\n✅ ARCHIVOS ESENCIALES DEL PROYECTO:")
    esenciales = [
        "manage.py",
        "requirements.txt",
        "db.sqlite3",
        ".gitignore",
        "LICENSE"
    ]
    
    for archivo in esenciales:
        if os.path.exists(archivo):
            print(f"   • {archivo} ✓")
        else:
            print(f"   • {archivo} ❌")
    
    # Directorios principales
    print(f"\n🗂️ DIRECTORIOS PRINCIPALES:")
    directorios = [
        "multiandamios/",
        "usuarios/",
        "productos/",
        "pedidos/",
        "recibos/",
        "chatbot/",
        "templates/",
        "static/",
        "media/"
    ]
    
    for directorio in directorios:
        if os.path.exists(directorio):
            print(f"   • {directorio} ✓")
        else:
            print(f"   • {directorio} ❌")

if __name__ == "__main__":
    main()
