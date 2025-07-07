#!/usr/bin/env python
"""
Diagnóstico específico para problema de selección de departamento/municipio
en el formulario de checkout
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import Departamento, Municipio
from django.test import Client
from django.urls import reverse
import json

def diagnostic_checkout_form():
    """Diagnóstico completo del formulario de checkout"""
    print("=== DIAGNÓSTICO: FORMULARIO DE CHECKOUT ===")
    
    # Verificar datos en BD
    print("\n1. VERIFICANDO DATOS EN BASE DE DATOS:")
    dept_count = Departamento.objects.count()
    muni_count = Municipio.objects.count()
    print(f"   Departamentos: {dept_count}")
    print(f"   Municipios: {muni_count}")
    
    if dept_count == 0:
        print("   ❌ ERROR: No hay departamentos cargados")
        return False
    
    if muni_count == 0:
        print("   ❌ ERROR: No hay municipios cargados")
        return False
    
    # Verificar API endpoints
    print("\n2. VERIFICANDO API ENDPOINTS:")
    client = Client()
    
    # Test API departamentos
    try:
        response = client.get('/api/departamentos/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API departamentos: {len(data.get('departamentos', []))} items")
        else:
            print(f"   ❌ API departamentos falló: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en API departamentos: {e}")
    
    # Test API municipios
    try:
        dept = Departamento.objects.first()
        response = client.get(f'/api/municipios/?departamento_id={dept.pk}')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API municipios: {len(data.get('municipios', []))} items")
        else:
            print(f"   ❌ API municipios falló: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en API municipios: {e}")
    
    # Verificar template de checkout
    print("\n3. VERIFICANDO TEMPLATE DE CHECKOUT:")
    try:
        response = client.get('/checkout/')
        if response.status_code == 200:
            print("   ✅ Template de checkout carga correctamente")
            # Verificar si contiene los selects necesarios
            content = response.content.decode('utf-8')
            if 'departamento' in content.lower():
                print("   ✅ Campo departamento encontrado en template")
            else:
                print("   ❌ Campo departamento NO encontrado en template")
            
            if 'municipio' in content.lower():
                print("   ✅ Campo municipio encontrado en template")
            else:
                print("   ❌ Campo municipio NO encontrado en template")
        else:
            print(f"   ❌ Template de checkout falló: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error al verificar template: {e}")
    
    # Verificar JavaScript
    print("\n4. VERIFICANDO JAVASCRIPT:")
    print("   📝 Revisa que el template contenga:")
    print("   - Script para cargar departamentos al cargar la página")
    print("   - Script para cargar municipios al cambiar departamento")
    print("   - Eventos onChange correctos")
    
    # Mostrar datos de ejemplo
    print("\n5. DATOS DE EJEMPLO DISPONIBLES:")
    print("   Departamentos:")
    for dept in Departamento.objects.all()[:5]:
        print(f"     - {dept.pk}: {dept.nombre}")
    
    print("   Municipios (primeros 5):")
    for muni in Municipio.objects.all()[:5]:
        print(f"     - {muni.pk}: {muni.nombre} ({muni.departamento.nombre})")
    
    return True

def generate_checkout_fix():
    """Generar código de ejemplo para arreglar el checkout"""
    print("\n=== SOLUCIÓN PARA CHECKOUT ===")
    
    print("\n1. JAVASCRIPT NECESARIO EN EL TEMPLATE:")
    print("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Cargar departamentos al cargar la página
    fetch('/api/departamentos/')
        .then(response => response.json())
        .then(data => {
            const departamentoSelect = document.getElementById('id_departamento');
            departamentoSelect.innerHTML = '<option value="">Seleccione un departamento</option>';
            
            data.departamentos.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.nombre;
                departamentoSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error cargando departamentos:', error));
    
    // Cargar municipios al cambiar departamento
    document.getElementById('id_departamento').addEventListener('change', function() {
        const departamentoId = this.value;
        const municipioSelect = document.getElementById('id_municipio');
        
        if (departamentoId) {
            fetch(`/api/municipios/?departamento_id=${departamentoId}`)
                .then(response => response.json())
                .then(data => {
                    municipioSelect.innerHTML = '<option value="">Seleccione un municipio</option>';
                    
                    data.municipios.forEach(muni => {
                        const option = document.createElement('option');
                        option.value = muni.id;
                        option.textContent = muni.nombre;
                        municipioSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error cargando municipios:', error));
        } else {
            municipioSelect.innerHTML = '<option value="">Primero seleccione un departamento</option>';
        }
    });
});
</script>
    """)
    
    print("\n2. HTML NECESARIO EN EL TEMPLATE:")
    print("""
<div class="form-group">
    <label for="id_departamento">Departamento:</label>
    <select id="id_departamento" name="departamento" class="form-control" required>
        <option value="">Seleccione un departamento</option>
    </select>
</div>

<div class="form-group">
    <label for="id_municipio">Municipio:</label>
    <select id="id_municipio" name="municipio" class="form-control" required>
        <option value="">Primero seleccione un departamento</option>
    </select>
</div>
    """)

def main():
    print("🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA DE CHECKOUT")
    print("=" * 60)
    
    success = diagnostic_checkout_form()
    
    if success:
        generate_checkout_fix()
        print("\n✅ DIAGNÓSTICO COMPLETADO")
        print("📝 Revisa los puntos marcados con ❌ para solucionar")
    else:
        print("\n❌ PROBLEMAS CRÍTICOS ENCONTRADOS")
        print("🔧 Primero carga los datos con: python cargar_divipola_produccion.py")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
