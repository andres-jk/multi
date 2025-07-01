#!/usr/bin/env python
"""
Script para probar el registro de usuarios corregido
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from django.test import Client
from usuarios.models import Usuario, Cliente

def test_registro_corregido():
    """Probar que el registro funcione sin errores de duplicación"""
    print("=== TEST DEL REGISTRO CORREGIDO ===\n")
    
    # Crear cliente de prueba
    client = Client()
    
    # Datos de prueba
    test_data = {
        'username': 'test_user_nuevo',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test_nuevo@example.com',
        'telefono': '123456789',
        'direccion': 'Calle Test 123',
        'password1': 'test_password_123',
        'password2': 'test_password_123',
    }
    
    print("📝 Datos de prueba:")
    for key, value in test_data.items():
        if 'password' not in key:
            print(f"    {key}: {value}")
    
    # Verificar que el usuario no existe
    if Usuario.objects.filter(username=test_data['username']).exists():
        print(f"⚠️  Usuario {test_data['username']} ya existe, eliminando...")
        Usuario.objects.filter(username=test_data['username']).delete()
    
    # Intentar registrar
    print("\n🔄 Intentando registrar...")
    response = client.post('/usuarios/registro/', test_data)
    
    print(f"📊 Respuesta: {response.status_code}")
    
    if response.status_code == 302:  # Redirección = éxito
        print("✅ Registro exitoso (redirección)")
        
        # Verificar que se creó el usuario
        try:
            usuario = Usuario.objects.get(username=test_data['username'])
            print(f"✅ Usuario creado: {usuario.username}")
            print(f"    Nombre: {usuario.first_name} {usuario.last_name}")
            print(f"    Email: {usuario.email}")
            print(f"    Rol: {usuario.rol}")
            
            # Verificar que se creó el cliente
            try:
                cliente = Cliente.objects.get(usuario=usuario)
                print(f"✅ Cliente creado: {cliente}")
                print(f"    Teléfono: {cliente.telefono}")
                print(f"    Dirección: {cliente.direccion}")
            except Cliente.DoesNotExist:
                print("❌ Cliente NO fue creado")
                
        except Usuario.DoesNotExist:
            print("❌ Usuario NO fue creado")
            
    else:
        print("❌ Error en el registro")
        content = response.content.decode('utf-8')
        if 'error' in content.lower():
            print("    Posibles errores en el formulario")
        
    # Test de usuario duplicado
    print("\n🔄 Intentando registrar usuario duplicado...")
    response2 = client.post('/usuarios/registro/', test_data)
    
    if response2.status_code == 200:  # Permanecer en la página = error esperado
        print("✅ Prevención de duplicados funciona (permaneció en la página)")
    else:
        print("⚠️  Inesperado: permitió registro duplicado")
    
    # Limpiar datos de prueba
    print("\n🧹 Limpiando datos de prueba...")
    Usuario.objects.filter(username=test_data['username']).delete()
    print("✅ Limpieza completada")

if __name__ == "__main__":
    test_registro_corregido()
