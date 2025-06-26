#!/usr/bin/env python
"""
Script para probar la vista de diagnóstico directamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from recibos.views import diagnostico_devoluciones

def test_diagnostico_view():
    print("=== PRUEBA DE VISTA DE DIAGNÓSTICO ===")
    
    try:
        # Simular una solicitud HTTP
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        # Crear una solicitud falsa
        request = HttpRequest()
        request.method = 'GET'
        request.user = AnonymousUser()
        
        # Crear y autenticar un usuario staff
        User = get_user_model()
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        
        request.user = admin_user
        
        # Llamar a la vista directamente
        response = diagnostico_devoluciones(request)
        
        print(f"✅ Vista ejecutada exitosamente")
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Template renderizado correctamente")
        
        # Si llegamos aquí, la vista funciona
        return True
        
    except Exception as e:
        print(f"❌ Error en la vista: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_diagnostico_view()
    if success:
        print("\n🎉 La vista de diagnóstico funciona correctamente!")
    else:
        print("\n💥 Hay problemas con la vista de diagnóstico")
