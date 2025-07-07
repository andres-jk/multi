#!/usr/bin/env python3
"""
Script para verificar y mostrar las URLs correctas de DIVIPOLA
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import Client
from usuarios.models_divipola import Departamento, Municipio

def verificar_urls_correctas():
    """
    Verificar cuáles son las URLs correctas funcionando
    """
    print("=== VERIFICACIÓN DE URLs CORRECTAS ===")
    
    client = Client()
    
    # URLs posibles para probar
    urls_departamentos = [
        '/usuarios/departamentos/',
        '/usuarios/api/departamentos/',
        '/api/departamentos/',
        '/departamentos/',
        '/usuarios/divipola/departamentos/',
    ]
    
    urls_municipios = [
        '/usuarios/municipios/1/',
        '/usuarios/api/municipios/1/',
        '/api/municipios/1/',
        '/municipios/1/',
        '/usuarios/divipola/municipios/1/',
    ]
    
    print("\n🔍 PROBANDO URLs DE DEPARTAMENTOS...")
    urls_departamentos_ok = []
    
    for url in urls_departamentos:
        try:
            response = client.get(url)
            status = response.status_code
            print(f"   {url}: {status}")
            
            if status == 200:
                urls_departamentos_ok.append(url)
                # Intentar parsear JSON
                try:
                    import json
                    data = json.loads(response.content.decode('utf-8'))
                    print(f"     ✅ JSON válido con {len(data)} elementos")
                except:
                    print(f"     ⚠️ Respuesta no es JSON")
            elif status == 404:
                print(f"     ❌ No encontrado")
            else:
                print(f"     ⚠️ Status {status}")
                
        except Exception as e:
            print(f"   {url}: Error - {e}")
    
    print("\n🔍 PROBANDO URLs DE MUNICIPIOS...")
    urls_municipios_ok = []
    
    # Obtener ID de departamento válido
    dept_id = 1
    if Departamento.objects.exists():
        dept_id = Departamento.objects.first().id
    
    for url_template in urls_municipios:
        url = url_template.replace('1', str(dept_id))
        try:
            response = client.get(url)
            status = response.status_code
            print(f"   {url}: {status}")
            
            if status == 200:
                urls_municipios_ok.append(url)
                # Intentar parsear JSON
                try:
                    import json
                    data = json.loads(response.content.decode('utf-8'))
                    if 'municipios' in data:
                        print(f"     ✅ JSON válido con {len(data['municipios'])} municipios")
                    else:
                        print(f"     ✅ JSON válido: {data}")
                except:
                    print(f"     ⚠️ Respuesta no es JSON")
            elif status == 404:
                print(f"     ❌ No encontrado")
            else:
                print(f"     ⚠️ Status {status}")
                
        except Exception as e:
            print(f"   {url}: Error - {e}")
    
    print("\n=== RESULTADOS ===")
    
    if urls_departamentos_ok:
        print(f"✅ URLs de departamentos funcionando: {len(urls_departamentos_ok)}")
        for url in urls_departamentos_ok:
            print(f"   - {url}")
    else:
        print("❌ No se encontraron URLs de departamentos funcionando")
    
    if urls_municipios_ok:
        print(f"✅ URLs de municipios funcionando: {len(urls_municipios_ok)}")
        for url in urls_municipios_ok:
            print(f"   - {url}")
    else:
        print("❌ No se encontraron URLs de municipios funcionando")
    
    # Verificar archivos de URLs
    print("\n🔍 VERIFICANDO ARCHIVOS DE CONFIGURACIÓN...")
    
    archivos_urls = [
        'usuarios/urls.py',
        'usuarios/urls_divipola.py',
        'multiandamios/urls.py'
    ]
    
    for archivo in archivos_urls:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo} existe")
        else:
            print(f"   ❌ {archivo} no existe")
    
    return urls_departamentos_ok, urls_municipios_ok

def generar_javascript_correcto(urls_dept, urls_muni):
    """
    Generar el JavaScript correcto para usar las URLs funcionando
    """
    print("\n=== JAVASCRIPT CORRECTO ===")
    
    if urls_dept and urls_muni:
        url_dept = urls_dept[0]
        url_muni = urls_muni[0].replace(str(Departamento.objects.first().id if Departamento.objects.exists() else 1), '${departamentoId}')
        
        js_code = f"""
// URLs correctas para DIVIPOLA
const DIVIPOLA_URLS = {{
    departamentos: '{url_dept}',
    municipios: '{url_muni}'
}};

// Función para cargar departamentos
function cargarDepartamentos() {{
    fetch(DIVIPOLA_URLS.departamentos)
        .then(response => response.json())
        .then(data => {{
            const select = document.getElementById('departamento');
            data.forEach(dept => {{
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.nombre;
                select.appendChild(option);
            }});
        }})
        .catch(error => console.error('Error cargando departamentos:', error));
}}

// Función para cargar municipios
function cargarMunicipios(departamentoId) {{
    const url = DIVIPOLA_URLS.municipios.replace('${{departamentoId}}', departamentoId);
    fetch(url)
        .then(response => response.json())
        .then(data => {{
            const select = document.getElementById('municipio');
            select.innerHTML = '<option value="">Seleccione municipio</option>';
            data.municipios.forEach(muni => {{
                const option = document.createElement('option');
                option.value = muni.id;
                option.textContent = muni.nombre;
                select.appendChild(option);
            }});
        }})
        .catch(error => console.error('Error cargando municipios:', error));
}}
"""
        print(js_code)
        
        # Guardar en archivo
        with open('javascript_divipola_correcto.js', 'w') as f:
            f.write(js_code)
        
        print("✅ JavaScript guardado en 'javascript_divipola_correcto.js'")
    
    else:
        print("❌ No se pueden generar URLs correctas - APIs no funcionan")

if __name__ == '__main__':
    urls_dept, urls_muni = verificar_urls_correctas()
    generar_javascript_correcto(urls_dept, urls_muni)
