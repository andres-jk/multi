#!/usr/bin/env python3
"""
Script para corregir ALLOWED_HOSTS automáticamente
"""

import os
import re

def fix_allowed_hosts():
    """
    Corregir ALLOWED_HOSTS en settings.py
    """
    settings_path = 'multiandamios/settings.py'
    
    print("=== CORRECCIÓN DE ALLOWED_HOSTS ===")
    
    if not os.path.exists(settings_path):
        print(f"❌ ERROR: {settings_path} no encontrado")
        return False
    
    # Hacer backup
    backup_path = settings_path + '.backup'
    with open(settings_path, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Backup creado: {backup_path}")
    
    # Patterns para buscar y reemplazar
    patterns = [
        (r"ALLOWED_HOSTS = \[\]", "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"),
        (r"ALLOWED_HOSTS = \['localhost', '127\.0\.0\.1'\]", "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"),
        (r"ALLOWED_HOSTS = \[\"localhost\", \"127\.0\.0\.1\"\]", "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"),
    ]
    
    modified = False
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"✅ Patrón encontrado y reemplazado: {pattern}")
            break
    
    if not modified:
        # Si no se encontró ningún patrón, buscar ALLOWED_HOSTS y agregar
        if 'ALLOWED_HOSTS' in content:
            print("⚠️ ALLOWED_HOSTS encontrado pero no coincide con patrones esperados")
            print("Mostrando líneas que contienen ALLOWED_HOSTS:")
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'ALLOWED_HOSTS' in line:
                    print(f"  Línea {i+1}: {line}")
        else:
            print("❌ ALLOWED_HOSTS no encontrado en el archivo")
    
    # Escribir el archivo modificado
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Archivo {settings_path} actualizado")
    
    # Verificar el cambio
    print("\n🔍 VERIFICACIÓN:")
    with open(settings_path, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if 'ALLOWED_HOSTS' in line:
            print(f"  Línea {i+1}: {line.strip()}")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Reinicia la aplicación web (Panel Web → Reload)")
    print("2. Visita: https://dalej.pythonanywhere.com/")
    print("3. Debería funcionar sin errores")
    
    return True

if __name__ == '__main__':
    fix_allowed_hosts()
