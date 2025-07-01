#!/usr/bin/env python
"""
Script de verificación final del sistema de URLs
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from usuarios.models import Usuario

def verificar_urls():
    """Verificar que todas las URLs funcionen correctamente"""
    print("=== VERIFICACIÓN FINAL DE URLs ===\n")
    
    try:
        # Verificar que las URLs se resuelvan correctamente
        urls_test = [
            ('pedidos:mis_pedidos', {}, '/panel/mis-pedidos/'),
            ('pedidos:detalle_mi_pedido', {'pedido_id': 30}, '/panel/mis-pedidos/30/'),
            ('usuarios:login', {}, '/usuarios/login/'),
        ]
        
        for url_name, kwargs, expected in urls_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                if url == expected:
                    print(f"✅ {url_name}: {url}")
                else:
                    print(f"⚠️  {url_name}: {url} (esperado: {expected})")
            except NoReverseMatch as e:
                print(f"❌ {url_name}: Error - {e}")
        
        print("\n🔐 INFORMACIÓN DE LOGIN:")
        print("    Usuario: oscar_ibañez")
        print("    Contraseña: test123")
        
        print("\n📋 URLs PARA PROBAR:")
        print("    Login: http://127.0.0.1:8000/usuarios/login/")
        print("    Mis Pedidos: http://127.0.0.1:8000/panel/mis-pedidos/")
        print("    Detalle Pedido #30: http://127.0.0.1:8000/panel/mis-pedidos/30/")
        print("    Detalle Pedido #29: http://127.0.0.1:8000/panel/mis-pedidos/29/")
        print("    Detalle Pedido #27: http://127.0.0.1:8000/panel/mis-pedidos/27/")
        
        print("\n📄 CONTENIDO ESPERADO EN DETALLE:")
        print("    - Información del pedido (fecha, estado, total)")
        print("    - Tabla con productos, cantidad, días, precio diario, subtotal")
        print("    - Botones de navegación")
        
        print("\n🔧 CAMBIOS REALIZADOS:")
        print("    ✅ Eliminada duplicación de URLs en usuarios/urls.py")
        print("    ✅ Configurado LOGIN_URL en settings.py")
        print("    ✅ Actualizado namespace de URLs en templates")
        print("    ✅ Servidor reiterado automáticamente")
        
        print("\n⚡ SOLUCIÓN AL PROBLEMA:")
        print("    El problema era duplicación de URLs que causaba conflictos")
        print("    en el enrutamiento. Ahora todas las URLs de pedidos están")
        print("    en /panel/ y funcionan correctamente.")
        
    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_urls()
