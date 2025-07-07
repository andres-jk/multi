#!/usr/bin/env python3
"""
Script de corrección forzada de ALLOWED_HOSTS
"""

import os
import re
import shutil

def fix_allowed_hosts_force():
    """
    Corrección forzada de ALLOWED_HOSTS con múltiples métodos
    """
    settings_path = 'multiandamios/settings.py'
    
    print("=== CORRECCIÓN FORZADA DE ALLOWED_HOSTS ===")
    
    # 1. Verificar archivo
    if not os.path.exists(settings_path):
        print(f"❌ ERROR: {settings_path} no encontrado")
        print(f"📂 Directorio actual: {os.getcwd()}")
        print("📋 Archivos disponibles:")
        try:
            files = os.listdir('.')
            for f in files[:10]:  # Mostrar primeros 10 archivos
                print(f"   - {f}")
        except:
            pass
        return False
    
    # 2. Hacer backup múltiple
    backup_path = settings_path + '.backup'
    if os.path.exists(backup_path):
        backup_path = settings_path + '.backup2'
    
    shutil.copy2(settings_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    # 3. Leer contenido
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 4. Mostrar contenido actual
    print("\n🔍 CONTENIDO ACTUAL DE ALLOWED_HOSTS:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'ALLOWED_HOSTS' in line:
            print(f"   Línea {i+1}: {line}")
    
    # 5. Patrones de reemplazo más agresivos
    patterns = [
        (r'ALLOWED_HOSTS\s*=\s*\[\]', "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"),
        (r'ALLOWED_HOSTS\s*=\s*\[.*?\]', "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"),
        (r'ALLOWED_HOSTS\s*=\s*\[.*?\n.*?\]', "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"),
    ]
    
    modified = False
    original_content = content
    
    for pattern, replacement in patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            modified = True
            print(f"✅ Patrón aplicado: {pattern}")
            break
    
    # 6. Si no se modificó, agregar al final
    if not modified:
        print("⚠️ No se encontró ALLOWED_HOSTS o no coincide con patrones")
        print("📝 Agregando ALLOWED_HOSTS al final del archivo")
        
        # Agregar al final
        content += '\n\n# Configuración para PythonAnywhere\n'
        content += "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']\n"
        modified = True
    
    # 7. Escribir archivo
    if modified:
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo {settings_path} modificado")
    else:
        print("❌ No se pudo modificar el archivo")
        return False
    
    # 8. Verificar cambio
    print("\n🔍 VERIFICACIÓN DEL CAMBIO:")
    with open(settings_path, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    lines = new_content.split('\n')
    found_correct = False
    
    for i, line in enumerate(lines):
        if 'ALLOWED_HOSTS' in line:
            print(f"   Línea {i+1}: {line}")
            if 'dalej.pythonanywhere.com' in line:
                found_correct = True
    
    if found_correct:
        print("✅ CORRECCIÓN EXITOSA: dalej.pythonanywhere.com está en ALLOWED_HOSTS")
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Reinicia la aplicación web (Panel Web → Reload)")
        print("2. Visita: https://dalej.pythonanywhere.com/")
        print("3. El error debería desaparecer")
        return True
    else:
        print("❌ CORRECCIÓN FALLIDA: dalej.pythonanywhere.com NO está en ALLOWED_HOSTS")
        
        # Mostrar diferencias
        print("\n📋 COMPARACIÓN:")
        print("ANTES:")
        print(original_content[:500] + "...")
        print("\nDESPUÉS:")
        print(new_content[:500] + "...")
        
        return False

if __name__ == '__main__':
    success = fix_allowed_hosts_force()
    if success:
        print("\n🎉 ¡CORRECCIÓN COMPLETADA!")
    else:
        print("\n❌ CORRECCIÓN FALLIDA - EDITA MANUALMENTE")
