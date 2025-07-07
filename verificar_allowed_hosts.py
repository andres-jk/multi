#!/usr/bin/env python3
"""
Verificar y mostrar el contenido de ALLOWED_HOSTS en settings.py
"""

import os
import sys

def verificar_allowed_hosts():
    """
    Verificar el contenido actual de ALLOWED_HOSTS
    """
    settings_path = 'multiandamios/settings.py'
    
    print("=== VERIFICACIÓN DE ALLOWED_HOSTS ===")
    
    if not os.path.exists(settings_path):
        print(f"❌ ERROR: {settings_path} no encontrado")
        return
    
    print(f"📁 Archivo: {settings_path}")
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    # Leer archivo
    with open(settings_path, 'r') as f:
        lines = f.readlines()
    
    print("\n🔍 BÚSQUEDA DE ALLOWED_HOSTS:")
    
    found_lines = []
    
    for i, line in enumerate(lines):
        if 'ALLOWED_HOSTS' in line:
            found_lines.append((i+1, line.strip()))
    
    if found_lines:
        print(f"✅ Encontradas {len(found_lines)} líneas con ALLOWED_HOSTS:")
        for line_num, content in found_lines:
            print(f"  Línea {line_num}: {content}")
    else:
        print("❌ No se encontró ALLOWED_HOSTS")
    
    # Mostrar contexto alrededor de ALLOWED_HOSTS
    print("\n📋 CONTEXTO COMPLETO:")
    
    for i, line in enumerate(lines):
        if 'ALLOWED_HOSTS' in line:
            start = max(0, i-2)
            end = min(len(lines), i+3)
            
            print(f"\n  Líneas {start+1}-{end}:")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"  {marker} {j+1}: {lines[j].rstrip()}")
    
    # Verificar si está correcto
    print("\n🎯 VERIFICACIÓN:")
    
    correct_hosts = "['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"
    
    for line_num, content in found_lines:
        if 'dalej.pythonanywhere.com' in content:
            print("✅ CORRECTO: dalej.pythonanywhere.com está en ALLOWED_HOSTS")
        else:
            print("❌ PROBLEMA: dalej.pythonanywhere.com NO está en ALLOWED_HOSTS")
            print(f"   Línea actual: {content}")
            print(f"   Debería ser: ALLOWED_HOSTS = {correct_hosts}")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    if not any('dalej.pythonanywhere.com' in content for _, content in found_lines):
        print("1. Ejecuta: nano multiandamios/settings.py")
        print("2. Busca la línea con ALLOWED_HOSTS")
        print(f"3. Cámbiala a: ALLOWED_HOSTS = {correct_hosts}")
        print("4. Guarda: Ctrl + X, Y, Enter")
        print("5. Reinicia la aplicación web")
    else:
        print("1. Reinicia la aplicación web (Panel Web → Reload)")
        print("2. Visita: https://dalej.pythonanywhere.com/")

if __name__ == '__main__':
    verificar_allowed_hosts()
