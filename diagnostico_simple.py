#!/usr/bin/env python3
"""
Diagnóstico simple de DIVIPOLA - funciona sin archivos adicionales
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import Client

def diagnostico_simple():
    """Diagnóstico básico de DIVIPOLA"""
    print("=== DIAGNÓSTICO SIMPLE DE DIVIPOLA ===")
    
    # 1. Verificar datos
    try:
        from usuarios.models_divipola import Departamento, Municipio
        
        dept_count = Departamento.objects.count()
        muni_count = Municipio.objects.count()
        
        print(f"📊 Departamentos: {dept_count}")
        print(f"📊 Municipios: {muni_count}")
        
        if dept_count > 0 and muni_count > 0:
            print("✅ Datos DIVIPOLA presentes")
        else:
            print("❌ Faltan datos DIVIPOLA")
            return
            
    except Exception as e:
        print(f"❌ Error accediendo a datos: {e}")
        return
    
    # 2. Probar URLs básicas
    client = Client()
    
    urls_prueba = [
        '/usuarios/departamentos/',
        '/usuarios/municipios/1/',
        '/api/departamentos/',
        '/api/municipios/1/',
    ]
    
    print("\n🔍 PROBANDO URLs:")
    urls_ok = []
    
    for url in urls_prueba:
        try:
            response = client.get(url)
            status = response.status_code
            print(f"   {url}: {status}")
            
            if status == 200:
                urls_ok.append(url)
                print(f"     ✅ Funciona")
            else:
                print(f"     ❌ No funciona")
                
        except Exception as e:
            print(f"   {url}: Error - {e}")
    
    print(f"\n📋 RESULTADO: {len(urls_ok)} URLs funcionando de {len(urls_prueba)}")
    
    if urls_ok:
        print("✅ URLs funcionando:")
        for url in urls_ok:
            print(f"   - {url}")
    else:
        print("❌ Ninguna URL de API funciona")
        print("🔧 Necesitas verificar la configuración de URLs")
    
    # 3. Verificar archivos
    print("\n📁 VERIFICANDO ARCHIVOS:")
    
    archivos_criticos = [
        'usuarios/urls.py',
        'usuarios/urls_divipola.py',
        'usuarios/views_divipola.py',
        'multiandamios/urls.py'
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} falta")
    
    # 4. Recomendaciones
    print("\n🎯 RECOMENDACIONES:")
    print("1. Reinicia la aplicación web (Panel → Reload)")
    print("2. Visita: https://dalej.pythonanywhere.com/checkout/")
    print("3. Verifica si los selectores funcionan en el navegador")
    
    if not urls_ok:
        print("\n🔧 Si los selectores no funcionan:")
        print("   - Verifica usuarios/urls.py")
        print("   - Verifica que las vistas estén correctas")
        print("   - Verifica que multiandamios/urls.py incluya usuarios.urls")

if __name__ == '__main__':
    diagnostico_simple()
