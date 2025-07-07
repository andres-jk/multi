#!/usr/bin/env python3
"""
Script final para verificar que MultiAndamios esté funcionando correctamente
Ejecutar después de todas las configuraciones
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
from usuarios.models import User
from productos.models import Producto
from pedidos.models import Pedido

def verificar_sistema_completo():
    """
    Verificación completa del sistema MultiAndamios
    """
    print("="*60)
    print("VERIFICACIÓN COMPLETA DE MULTIANDAMIOS")
    print("="*60)
    
    errores = []
    exitos = []
    
    # 1. Verificar base de datos
    print("\n1. 🔍 VERIFICANDO BASE DE DATOS...")
    try:
        users = User.objects.count()
        print(f"   👥 Usuarios: {users}")
        if users > 0:
            exitos.append("Base de datos de usuarios funcional")
        else:
            errores.append("No hay usuarios en la base de datos")
    except Exception as e:
        errores.append(f"Error en usuarios: {e}")
    
    # 2. Verificar DIVIPOLA
    print("\n2. 🌍 VERIFICANDO DIVIPOLA...")
    try:
        depts = Departamento.objects.count()
        munis = Municipio.objects.count()
        print(f"   📍 Departamentos: {depts}")
        print(f"   🏘️  Municipios: {munis}")
        
        if depts > 0 and munis > 0:
            exitos.append("DIVIPOLA cargado correctamente")
        else:
            errores.append("DIVIPOLA no está cargado")
    except Exception as e:
        errores.append(f"Error en DIVIPOLA: {e}")
    
    # 3. Verificar productos
    print("\n3. 📦 VERIFICANDO PRODUCTOS...")
    try:
        productos = Producto.objects.count()
        print(f"   📦 Productos: {productos}")
        if productos > 0:
            exitos.append("Sistema de productos funcional")
        else:
            errores.append("No hay productos en el sistema")
    except Exception as e:
        errores.append(f"Error en productos: {e}")
    
    # 4. Verificar pedidos
    print("\n4. 🛒 VERIFICANDO PEDIDOS...")
    try:
        pedidos = Pedido.objects.count()
        print(f"   🛒 Pedidos: {pedidos}")
        exitos.append("Sistema de pedidos funcional")
    except Exception as e:
        errores.append(f"Error en pedidos: {e}")
    
    # 5. Verificar API endpoints
    print("\n5. 🔗 VERIFICANDO API ENDPOINTS...")
    client = Client()
    
    try:
        # Test endpoint de departamentos
        response = client.get('/usuarios/departamentos/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API departamentos: {len(data)} departamentos")
            exitos.append("API de departamentos funcional")
        else:
            errores.append(f"API departamentos falla: {response.status_code}")
    except Exception as e:
        errores.append(f"Error en API departamentos: {e}")
    
    try:
        # Test endpoint de municipios
        if Departamento.objects.exists():
            dept_id = Departamento.objects.first().id
            response = client.get(f'/usuarios/municipios/{dept_id}/')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API municipios: {len(data['municipios'])} municipios")
                exitos.append("API de municipios funcional")
            else:
                errores.append(f"API municipios falla: {response.status_code}")
    except Exception as e:
        errores.append(f"Error en API municipios: {e}")
    
    # 6. Verificar páginas principales
    print("\n6. 🌐 VERIFICANDO PÁGINAS PRINCIPALES...")
    
    paginas = [
        ('/', 'Página principal'),
        ('/productos/', 'Catálogo de productos'),
        ('/checkout/', 'Checkout'),
        ('/admin/', 'Panel de administración'),
    ]
    
    for url, nombre in paginas:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # 302 para redirects (login)
                print(f"   ✅ {nombre}: OK ({response.status_code})")
                exitos.append(f"{nombre} accesible")
            else:
                print(f"   ❌ {nombre}: Error {response.status_code}")
                errores.append(f"{nombre} devuelve error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {nombre}: Error {e}")
            errores.append(f"{nombre} genera excepción: {e}")
    
    # 7. Verificar archivos estáticos
    print("\n7. 📁 VERIFICANDO ARCHIVOS ESTÁTICOS...")
    
    from django.conf import settings
    import os
    
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root and os.path.exists(static_root):
        archivos_static = os.listdir(static_root)
        print(f"   📁 Archivos estáticos: {len(archivos_static)} directorios/archivos")
        
        # Verificar CSS específico
        css_path = os.path.join(static_root, 'css')
        if os.path.exists(css_path):
            css_files = os.listdir(css_path)
            print(f"   🎨 Archivos CSS: {len(css_files)}")
            exitos.append("Archivos estáticos configurados")
        else:
            errores.append("No se encontraron archivos CSS")
    else:
        errores.append("STATIC_ROOT no existe o no está configurado")
    
    # RESUMEN FINAL
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    print(f"\n✅ ÉXITOS ({len(exitos)}):")
    for exito in exitos:
        print(f"   ✅ {exito}")
    
    if errores:
        print(f"\n❌ ERRORES ({len(errores)}):")
        for error in errores:
            print(f"   ❌ {error}")
    
    print(f"\n🎯 RESULTADO: {len(exitos)} éxitos, {len(errores)} errores")
    
    if len(errores) == 0:
        print("\n🚀 ¡MULTIANDAMIOS ESTÁ FUNCIONANDO PERFECTAMENTE!")
        print("✅ Puedes probar el sitio en: https://dalej.pythonanywhere.com/")
    elif len(errores) <= 2:
        print("\n⚠️ MultiAndamios funciona con errores menores")
        print("✅ Puedes probar el sitio en: https://dalej.pythonanywhere.com/")
    else:
        print("\n❌ Hay problemas que necesitan atención")
        print("🔧 Revisa los errores listados arriba")
    
    return len(errores) == 0

if __name__ == '__main__':
    try:
        verificar_sistema_completo()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
