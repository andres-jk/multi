#!/usr/bin/env python3
"""
Diagnóstico y corrección de APIs de DIVIPOLA
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from usuarios.models_divipola import Departamento, Municipio

def diagnosticar_apis_divipola():
    """
    Diagnosticar y mostrar las URLs correctas de las APIs de DIVIPOLA
    """
    print("=== DIAGNÓSTICO DE APIs DIVIPOLA ===")
    
    client = Client()
    
    # 1. Verificar URLs disponibles
    print("\n1. 🔍 VERIFICANDO URLs DISPONIBLES...")
    
    # URLs a probar
    urls_prueba = [
        '/usuarios/departamentos/',
        '/usuarios/municipios/1/',
        '/api/departamentos/',
        '/api/municipios/1/',
        '/usuarios/api/departamentos/',
        '/usuarios/api/municipios/1/',
    ]
    
    for url in urls_prueba:
        try:
            response = client.get(url)
            print(f"   {url}: {response.status_code}")
        except Exception as e:
            print(f"   {url}: Error - {e}")
    
    # 2. Verificar URLs con reverse
    print("\n2. 🔍 VERIFICANDO URLs CON REVERSE...")
    
    try:
        # Intentar obtener URLs con reverse
        from django.urls import reverse
        
        urls_reverse = [
            'usuarios:departamentos',
            'usuarios:municipios',
            'api_departamentos',
            'api_municipios',
        ]
        
        for url_name in urls_reverse:
            try:
                url = reverse(url_name)
                print(f"   {url_name}: {url}")
            except Exception as e:
                print(f"   {url_name}: Error - {e}")
                
    except Exception as e:
        print(f"   Error general en reverse: {e}")
    
    # 3. Verificar vistas directamente
    print("\n3. 🔍 VERIFICANDO VISTAS DIRECTAMENTE...")
    
    try:
        from usuarios.views_divipola import obtener_departamentos, obtener_municipios_por_departamento
        
        # Llamar vista de departamentos
        response_dept = obtener_departamentos(client.get('/').wsgi_request)
        print(f"   Vista departamentos: {response_dept.status_code}")
        
        # Llamar vista de municipios
        if Departamento.objects.exists():
            dept_id = Departamento.objects.first().id
            response_muni = obtener_municipios_por_departamento(client.get('/').wsgi_request, dept_id)
            print(f"   Vista municipios: {response_muni.status_code}")
        
    except Exception as e:
        print(f"   Error en vistas directas: {e}")
    
    # 4. Mostrar datos disponibles
    print("\n4. 📊 DATOS DISPONIBLES...")
    
    try:
        departamentos = Departamento.objects.all()
        print(f"   Departamentos: {departamentos.count()}")
        
        for dept in departamentos[:3]:
            municipios_dept = Municipio.objects.filter(departamento=dept)
            print(f"   - {dept.nombre}: {municipios_dept.count()} municipios")
            
    except Exception as e:
        print(f"   Error al obtener datos: {e}")
    
    # 5. Verificar archivo urls.py
    print("\n5. 🔍 VERIFICANDO CONFIGURACIÓN DE URLs...")
    
    try:
        from usuarios import urls as usuarios_urls
        print("   usuarios/urls.py encontrado")
        
        # Verificar patrones
        if hasattr(usuarios_urls, 'urlpatterns'):
            print(f"   Patrones encontrados: {len(usuarios_urls.urlpatterns)}")
        
    except Exception as e:
        print(f"   Error en urls.py: {e}")
    
    print("\n=== RECOMENDACIONES ===")
    print("1. Verificar que usuarios/urls.py tenga las URLs de DIVIPOLA")
    print("2. Verificar que multiandamios/urls.py incluya usuarios.urls")
    print("3. Probar URLs manualmente en el navegador")
    print("4. Verificar que las vistas de DIVIPOLA estén correctas")

if __name__ == '__main__':
    diagnosticar_apis_divipola()
