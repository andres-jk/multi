#!/usr/bin/env python
"""
Script para verificar que los estilos CSS personalizados se apliquen correctamente en el admin de Django.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

def verificar_archivos_css():
    """Verificar que los archivos CSS existan"""
    print("🔍 Verificando archivos CSS...")
    
    css_path = Path("static/admin/css/admin_custom.css")
    if css_path.exists():
        print(f"✅ Archivo CSS encontrado: {css_path}")
        
        # Leer el contenido del CSS
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar que contiene los estilos de focus
        if ':focus' in content:
            print("✅ Archivo CSS contiene estilos de :focus")
        else:
            print("❌ Archivo CSS NO contiene estilos de :focus")
            
        if 'background-color: #4a4a4a' in content:
            print("✅ Archivo CSS contiene el color de fondo gris oscuro")
        else:
            print("❌ Archivo CSS NO contiene el color de fondo gris oscuro")
            
        # Contar el número de reglas de focus
        focus_count = content.count(':focus')
        print(f"📊 Número de reglas :focus encontradas: {focus_count}")
        
    else:
        print(f"❌ Archivo CSS NO encontrado: {css_path}")

def verificar_configuracion_admin():
    """Verificar que los modelos admin tengan el CSS configurado"""
    print("\n🔍 Verificando configuración de modelos admin...")
    
    from productos.admin import ProductoAdmin
    from pedidos.admin import PedidoAdmin, DetallePedidoAdmin
    from usuarios.admin import UsuarioAdmin, ClienteAdmin, CarritoItemAdmin
    from recibos.admin import ReciboObraAdmin, DetalleReciboObraAdmin, EstadoProductoIndividualAdmin
    
    admins_to_check = [
        ('ProductoAdmin', ProductoAdmin),
        ('PedidoAdmin', PedidoAdmin),
        ('DetallePedidoAdmin', DetallePedidoAdmin),
        ('UsuarioAdmin', UsuarioAdmin),
        ('ClienteAdmin', ClienteAdmin),
        ('CarritoItemAdmin', CarritoItemAdmin),
        ('ReciboObraAdmin', ReciboObraAdmin),
        ('DetalleReciboObraAdmin', DetalleReciboObraAdmin),
        ('EstadoProductoIndividualAdmin', EstadoProductoIndividualAdmin),
    ]
    
    for name, admin_class in admins_to_check:
        if hasattr(admin_class, 'Media'):
            if hasattr(admin_class.Media, 'css'):
                if 'all' in admin_class.Media.css:
                    css_files = admin_class.Media.css['all']
                    if 'admin/css/admin_custom.css' in css_files:
                        print(f"✅ {name} tiene CSS personalizado configurado")
                    else:
                        print(f"❌ {name} NO tiene admin_custom.css configurado")
                else:
                    print(f"❌ {name} NO tiene CSS 'all' configurado")
            else:
                print(f"❌ {name} NO tiene CSS configurado")
        else:
            print(f"❌ {name} NO tiene Media configurado")

def main():
    print("🧪 VERIFICACIÓN DE CSS PERSONALIZADO DEL ADMIN")
    print("=" * 50)
    
    verificar_archivos_css()
    verificar_configuracion_admin()
    
    print("\n" + "=" * 50)
    print("✅ Verificación completada.")
    print("\n📝 INSTRUCCIONES PARA PROBAR:")
    print("1. Inicia el servidor: python manage.py runserver")
    print("2. Ve al admin: http://127.0.0.1:8000/admin/")
    print("3. Entra a cualquier modelo (ej: productos)")
    print("4. Haz click en cualquier campo de entrada")
    print("5. El fondo debe cambiar a gris oscuro (#4a4a4a)")

if __name__ == "__main__":
    main()
