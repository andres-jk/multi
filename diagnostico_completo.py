#!/usr/bin/env python3
"""
Script de diagnóstico completo para MultiAndamios
Verifica el estado de todos los componentes críticos del sistema.
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Ejecuta un comando y retorna el resultado."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}: OK")
            return True, result.stdout
        else:
            print(f"❌ {description}: ERROR")
            print(f"   Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description}: EXCEPCIÓN")
        print(f"   Error: {e}")
        return False, str(e)

def check_file_exists(filepath, description):
    """Verifica si un archivo existe."""
    print(f"🔍 Verificando {description}...")
    if os.path.exists(filepath):
        print(f"✅ {description}: EXISTE")
        return True
    else:
        print(f"❌ {description}: NO EXISTE")
        return False

def check_import(module_path, class_name):
    """Verifica si una clase puede ser importada."""
    print(f"🔍 Verificando importación de {class_name}...")
    try:
        # Usar importlib para importar dinámicamente
        import importlib
        module = importlib.import_module(module_path)
        if hasattr(module, class_name):
            print(f"✅ {class_name}: IMPORTABLE")
            return True
        else:
            print(f"❌ {class_name}: NO ENCONTRADA EN EL MÓDULO")
            return False
    except ImportError as e:
        print(f"❌ {class_name}: ERROR DE IMPORTACIÓN")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {class_name}: ERROR GENERAL")
        print(f"   Error: {e}")
        return False

def main():
    print("🔧 DIAGNÓSTICO COMPLETO DEL SISTEMA MULTIANDAMIOS")
    print("=" * 60)
    
    # Lista de verificaciones
    checks = []
    
    # 1. Verificar archivos críticos
    print("\n📁 VERIFICANDO ARCHIVOS CRÍTICOS...")
    files_to_check = [
        ('manage.py', 'Archivo principal de Django'),
        ('usuarios/forms.py', 'Formularios de usuarios'),
        ('usuarios/views_empleados.py', 'Vistas de empleados'),
        ('usuarios/urls.py', 'URLs de usuarios'),
        ('templates/base.html', 'Template base'),
        ('static/css/estilos.css', 'Estilos principales'),
        ('multiandamios/settings.py', 'Configuración de Django'),
    ]
    
    for filepath, description in files_to_check:
        result = check_file_exists(filepath, description)
        checks.append((description, result))
    
    # 2. Verificar importaciones críticas
    print("\n📦 VERIFICANDO IMPORTACIONES...")
    imports_to_check = [
        ('usuarios.forms', 'EmpleadoForm'),
        ('usuarios.views_empleados', 'lista_empleados'),
        ('usuarios.models', 'Usuario'),
        ('productos.models', 'Producto'),
        ('pedidos.models', 'Pedido'),
    ]
    
    for module_path, class_name in imports_to_check:
        result = check_import(module_path, class_name)
        checks.append((f"Importación {class_name}", result))
    
    # 3. Verificar configuración de Django
    print("\n⚙️ VERIFICANDO CONFIGURACIÓN DE DJANGO...")
    django_checks = [
        ('python manage.py check', 'Verificación general de Django'),
        ('python manage.py check --deploy', 'Verificación de despliegue'),
    ]
    
    for cmd, description in django_checks:
        result, output = run_command(cmd, description)
        checks.append((description, result))
    
    # 4. Verificar estructura de URLs
    print("\n🔗 VERIFICANDO URLs...")
    if os.path.exists('usuarios/urls.py'):
        try:
            with open('usuarios/urls.py', 'r', encoding='utf-8') as f:
                content = f.read()
                empleados_urls = [
                    'empleados/',
                    'empleados/crear/',
                    'empleados/editar/',
                    'empleados/eliminar/'
                ]
                for url in empleados_urls:
                    if url in content:
                        print(f"✅ URL {url}: ENCONTRADA")
                        checks.append((f"URL {url}", True))
                    else:
                        print(f"❌ URL {url}: NO ENCONTRADA")
                        checks.append((f"URL {url}", False))
        except Exception as e:
            print(f"❌ Error al verificar URLs: {e}")
            checks.append(("Verificación de URLs", False))
    
    # 5. Verificar templates de empleados
    print("\n📄 VERIFICANDO TEMPLATES DE EMPLEADOS...")
    empleados_templates = [
        'usuarios/templates/usuarios/empleados/lista.html',
        'usuarios/templates/usuarios/empleados/crear.html',
        'usuarios/templates/usuarios/empleados/editar.html',
        'usuarios/templates/usuarios/empleados/detalle.html',
    ]
    
    for template in empleados_templates:
        result = check_file_exists(template, f"Template {os.path.basename(template)}")
        checks.append((f"Template {os.path.basename(template)}", result))
    
    # 6. Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\n✅ Verificaciones exitosas: {passed}/{total}")
    print(f"❌ Verificaciones fallidas: {total - passed}/{total}")
    
    if total - passed > 0:
        print("\n❌ VERIFICACIONES FALLIDAS:")
        for description, status in checks:
            if not status:
                print(f"   - {description}")
    
    print("\n🎯 RECOMENDACIONES:")
    if passed == total:
        print("   ✅ ¡Todas las verificaciones pasaron! El sistema está listo.")
        print("   📋 Próximo paso: Recargar la aplicación web en PythonAnywhere")
    else:
        print("   🔧 Hay problemas que necesitan corrección.")
        print("   📋 Ejecuta los scripts de corrección correspondientes:")
        print("      - sync_forms.py (para problemas con formularios)")
        print("      - actualizar_servidor_completo.sh (para actualización completa)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
