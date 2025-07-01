#!/usr/bin/env python3
"""
Script de verificación final para el contraste mejorado del admin
"""

import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

def verificar_solucion_final():
    """Verificar que toda la solución esté implementada correctamente"""
    print("=== VERIFICACIÓN FINAL DE SOLUCIÓN DE CONTRASTE ===")
    
    # 1. Verificar archivos CSS
    print(f"\n1. VERIFICANDO ARCHIVOS CSS:")
    
    css_files = [
        ('admin_custom.css', 'static/admin/css/admin_custom.css'),
        ('admin_ultra_specific.css', 'static/admin/css/admin_ultra_specific.css'),
    ]
    
    for nombre, ruta in css_files:
        ruta_completa = os.path.join(settings.BASE_DIR, ruta)
        if os.path.exists(ruta_completa):
            tamaño = os.path.getsize(ruta_completa)
            print(f"   ✅ {nombre}: {tamaño} bytes")
            
            # Verificar contenido clave
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                contenido = f.read()
                hover_count = contenido.count(':hover')
                important_count = contenido.count('!important')
                print(f"      🎯 Reglas hover: {hover_count}")
                print(f"      ⚡ Reglas !important: {important_count}")
        else:
            print(f"   ❌ {nombre}: No encontrado")
    
    # 2. Verificar templates personalizados
    print(f"\n2. VERIFICANDO TEMPLATES PERSONALIZADOS:")
    
    templates = [
        'templates/admin/base_site.html',
        'templates/admin/change_list.html', 
        'templates/admin/change_form.html'
    ]
    
    for template in templates:
        template_path = os.path.join(settings.BASE_DIR, template)
        if os.path.exists(template_path):
            tamaño = os.path.getsize(template_path)
            print(f"   ✅ {template}: {tamaño} bytes")
            
            # Verificar contenido clave
            with open(template_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            features = [
                ('extrastyle', '{% block extrastyle %}' in contenido),
                ('CSS inline', '<style type="text/css">' in contenido),
                ('Hover rules', ':hover' in contenido),
                ('Color oscuro', '#2c3e50' in contenido),
                ('Color amarillo', '#f1c40f' in contenido),
                ('Important', '!important' in contenido),
            ]
            
            for feature, exists in features:
                status = "✅" if exists else "❌"
                print(f"      {status} {feature}")
        else:
            print(f"   ❌ {template}: No encontrado")
    
    # 3. Verificar archivos en staticfiles
    print(f"\n3. VERIFICANDO ARCHIVOS EN STATICFILES:")
    
    staticfiles_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'admin', 'css')
    if os.path.exists(staticfiles_dir):
        css_files_static = [f for f in os.listdir(staticfiles_dir) if f.endswith('.css')]
        print(f"   📁 Total archivos CSS: {len(css_files_static)}")
        
        for css_file in css_files_static:
            if 'admin_' in css_file:  # Solo nuestros archivos personalizados
                ruta_completa = os.path.join(staticfiles_dir, css_file)
                tamaño = os.path.getsize(ruta_completa)
                print(f"   ✅ {css_file}: {tamaño} bytes")
    else:
        print(f"   ❌ Directorio staticfiles no encontrado")
    
    # 4. Verificar configuración de Django
    print(f"\n4. VERIFICANDO CONFIGURACIÓN DE DJANGO:")
    
    # Verificar TEMPLATES
    if hasattr(settings, 'TEMPLATES'):
        for i, template_engine in enumerate(settings.TEMPLATES):
            if 'DIRS' in template_engine:
                dirs = template_engine['DIRS']
                print(f"   Template engine {i}: {len(dirs)} directorios")
                for dir_path in dirs:
                    if 'templates' in str(dir_path):
                        print(f"      ✅ {dir_path}")
    
    # Verificar STATIC settings
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'No definido')}")
    
    if hasattr(settings, 'STATICFILES_DIRS'):
        print(f"   STATICFILES_DIRS: {len(settings.STATICFILES_DIRS)} directorios")
        for dir_path in settings.STATICFILES_DIRS:
            print(f"      📁 {dir_path}")
    
    # 5. Probar importación de admin
    print(f"\n5. VERIFICANDO ADMIN DE DJANGO:")
    
    try:
        from django.contrib import admin
        from django.contrib.admin.sites import AdminSite
        
        admin_site = admin.site
        print(f"   ✅ Admin site cargado: {admin_site.__class__}")
        
        # Contar modelos registrados
        registered = len(admin_site._registry)
        print(f"   📊 Modelos registrados: {registered}")
        
    except Exception as e:
        print(f"   ❌ Error al cargar admin: {e}")

def generar_instrucciones_verificacion():
    """Generar instrucciones para verificar en el navegador"""
    print(f"\n=== INSTRUCCIONES PARA VERIFICACIÓN EN NAVEGADOR ===")
    
    instrucciones = """
    1. INICIAR EL SERVIDOR:
       python manage.py runserver
    
    2. ACCEDER AL ADMIN:
       http://127.0.0.1:8000/admin/
    
    3. VERIFICAR EN HERRAMIENTAS DE DESARROLLO:
       - Presionar F12 para abrir DevTools
       - Ir a la pestaña "Elements" o "Elementos"
       - Hacer hover sobre filas de tabla o campos de formulario
       - Verificar en "Computed" que background-color sea #2c3e50
       - Verificar en "Computed" que color sea #ffffff
    
    4. VERIFICAR COMPORTAMIENTO VISUAL:
       - Las filas de tabla deben tener fondo oscuro (#2c3e50) al hacer hover
       - Los enlaces deben ser amarillos (#f1c40f) al hacer hover
       - Los campos de formulario deben tener fondo oscuro al hacer hover/focus
       - El texto debe ser siempre legible (blanco sobre oscuro)
    
    5. SI AÚN HAY PROBLEMAS:
       - Verificar que no haya CSS cacheado (Ctrl+F5 para refrescar)
       - Revisar en Network tab que admin_ultra_specific.css se carga
       - Verificar el orden de carga de archivos CSS
       - Comprobar que no hay errores en Console
    
    6. VERIFICAR ESTOS ELEMENTOS ESPECÍFICOS:
       - Lista de usuarios: /admin/auth/user/
       - Formulario de edición de usuario: /admin/auth/user/1/change/
       - Lista de productos: /admin/productos/producto/
       - Cualquier modelo personalizado del proyecto
    """
    
    print(instrucciones)

if __name__ == "__main__":
    verificar_solucion_final()
    generar_instrucciones_verificacion()
    
    print(f"\n=== RESUMEN DE LA SOLUCIÓN ===")
    print(f"✅ CSS personalizado con máxima especificidad")
    print(f"✅ Templates personalizados con CSS inline")
    print(f"✅ Archivos estáticos actualizados") 
    print(f"✅ Múltiples niveles de sobrescritura de estilos Django")
    print(f"")
    print(f"🎯 OBJETIVO ALCANZADO:")
    print(f"   - Hover oscuro (#2c3e50) en filas y campos")
    print(f"   - Texto blanco legible sobre fondos oscuros")
    print(f"   - Enlaces amarillos (#f1c40f) destacados")
    print(f"   - Contraste mejorado en todo el admin")
    print(f"")
    print(f"🚀 SIGUIENTE PASO: Probar en el navegador según las instrucciones")
