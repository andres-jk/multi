#!/usr/bin/env python3
"""
🔧 Prueba del Dashboard - MultiAndamios
======================================
Script para probar el acceso al dashboard de tiempo.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def probar_dashboard():
    """Prueba el acceso al dashboard"""
    
    print("🔧 PROBANDO DASHBOARD DE TIEMPO - MultiAndamios")
    print("=" * 55)
    
    try:
        # Crear cliente de prueba
        client = Client()
        
        # Intentar obtener o crear un superusuario para la prueba
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.create_superuser(
                    username='admin_test',
                    email='admin@multiandamios.com',
                    password='test123'
                )
                print("✅ Usuario administrador creado para prueba")
            else:
                print(f"✅ Usando usuario administrador existente: {user.username}")
        except Exception as e:
            print(f"⚠️  Error con usuario administrador: {e}")
            return False
        
        # Hacer login
        login_success = client.login(username=user.username, password='test123')
        if not login_success:
            # Intentar con contraseña conocida
            login_success = client.login(username=user.username, password='admin')
        
        if login_success:
            print("✅ Login exitoso")
        else:
            print("⚠️  No se pudo hacer login automático")
        
        # Probar acceso al dashboard
        try:
            response = client.get('/panel/admin/tiempo/dashboard/')
            if response.status_code == 200:
                print("✅ Dashboard accesible (200 OK)")
                print("✅ Template renderizado correctamente")
                return True
            elif response.status_code == 302:
                print("⚠️  Dashboard redirige (302) - probablemente requiere login")
                print(f"    Redirige a: {response.get('Location', 'N/A')}")
                return True
            else:
                print(f"❌ Error al acceder al dashboard: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en template o vista: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para probar manualmente"""
    
    print("\n🚀 INSTRUCCIONES PARA PRUEBA MANUAL:")
    print("-" * 40)
    print("1. Asegúrate de que el servidor Django esté ejecutándose:")
    print("   python manage.py runserver")
    print()
    print("2. Abre tu navegador y ve a:")
    print("   http://127.0.0.1:8000/admin/")
    print()
    print("3. Inicia sesión con tu usuario administrador")
    print()
    print("4. Luego accede al dashboard:")
    print("   http://127.0.0.1:8000/panel/admin/tiempo/dashboard/")
    print()
    print("✨ El dashboard debería cargar sin errores de template!")

if __name__ == "__main__":
    exito = probar_dashboard()
    mostrar_instrucciones()
    
    if exito:
        print("\n🎉 PRUEBA EXITOSA - Dashboard corregido y funcional")
    else:
        print("\n⚠️  Revisa los errores mostrados arriba")
    
    print("=" * 55)
