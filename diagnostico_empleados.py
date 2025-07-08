#!/usr/bin/env python3
"""
Script para verificar y solucionar problemas con URLs de empleados
Ejecutar en PythonAnywhere después del git pull
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/Dalej/multi')  # Ajustar según tu estructura
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

def verificar_urls_empleados():
    """Verificar que todas las URLs de empleados funcionen"""
    print("🔍 VERIFICANDO URLs DE EMPLEADOS")
    print("=" * 50)
    
    urls_empleados = [
        ('usuarios:lista_empleados', 'Lista de empleados'),
        ('usuarios:crear_empleado', 'Crear empleado'),
    ]
    
    for url_name, descripcion in urls_empleados:
        try:
            url = reverse(url_name)
            print(f"✅ {descripcion}: {url}")
        except Exception as e:
            print(f"❌ {descripcion}: ERROR - {e}")
    
    print("\n🧪 PROBANDO ACCESO CON USUARIO ADMIN")
    print("=" * 50)
    
    User = get_user_model()
    
    try:
        # Buscar usuario admin
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            print("❌ No se encontró usuario administrador")
            return
        
        print(f"👤 Usuario admin encontrado: {admin_user.username}")
        
        # Crear cliente de prueba
        client = Client()
        client.force_login(admin_user)
        
        # Probar acceso a lista de empleados
        response = client.get('/empleados/')
        print(f"📄 Acceso a /empleados/: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Lista de empleados carga correctamente")
        elif response.status_code == 302:
            print(f"🔄 Redirección a: {response.url}")
        else:
            print(f"❌ Error en lista de empleados: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

def verificar_templates():
    """Verificar que existan los templates necesarios"""
    print("\n📁 VERIFICANDO TEMPLATES")
    print("=" * 50)
    
    templates_requeridos = [
        'usuarios/lista_empleados.html',
        'usuarios/crear_empleado.html',
        'usuarios/editar_empleado.html',
        'usuarios/detalle_empleado.html',
    ]
    
    base_path = '/home/Dalej/multi/usuarios/templates/'
    
    for template in templates_requeridos:
        template_path = os.path.join(base_path, template)
        if os.path.exists(template_path):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - NO ENCONTRADO")

def verificar_views():
    """Verificar que existan las vistas necesarias"""
    print("\n🔧 VERIFICANDO VISTAS")
    print("=" * 50)
    
    try:
        from usuarios import views_empleados
        
        vistas_requeridas = [
            'lista_empleados',
            'crear_empleado',
            'editar_empleado',
            'detalle_empleado',
        ]
        
        for vista in vistas_requeridas:
            if hasattr(views_empleados, vista):
                print(f"✅ {vista}")
            else:
                print(f"❌ {vista} - NO ENCONTRADA")
                
    except Exception as e:
        print(f"❌ Error al importar views_empleados: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO COMPLETO DE EMPLEADOS")
    print("=" * 60)
    
    verificar_views()
    verificar_templates()
    verificar_urls_empleados()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("Si hay errores, ejecuta: python manage.py check --deploy")
    print("=" * 60)
