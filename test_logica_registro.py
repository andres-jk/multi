#!/usr/bin/env python
"""
Script simple para verificar la corrección del registro
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from usuarios.models import Usuario, Cliente
from usuarios.forms import RegistroForm

def test_logica_registro():
    """Probar la lógica de registro sin hacer requests HTTP"""
    print("=== TEST DE LÓGICA DE REGISTRO ===\n")
    
    # Datos de prueba
    form_data = {
        'username': 'test_usuario_nuevo',
        'first_name': 'Test',
        'last_name': 'Usuario',
        'email': 'test@nuevo.com',
        'telefono': '123456789',
        'direccion': 'Calle Test 123',
        'password1': 'test_password_123',
        'password2': 'test_password_123',
    }
    
    # Limpiar usuario existente si lo hay
    Usuario.objects.filter(username=form_data['username']).delete()
    
    print("🔄 Probando formulario de registro...")
    
    # Crear y validar formulario
    form = RegistroForm(data=form_data)
    
    if form.is_valid():
        print("✅ Formulario válido")
        
        # Simular el proceso de guardado
        usuario = form.save()
        print(f"✅ Usuario creado: {usuario.username}")
        
        # Simular creación de cliente
        cliente, created = Cliente.objects.get_or_create(
            usuario=usuario,
            defaults={
                'telefono': form.cleaned_data.get('telefono', ''),
                'direccion': form.cleaned_data.get('direccion', '')
            }
        )
        
        if created:
            print(f"✅ Cliente creado: {cliente}")
        else:
            print(f"ℹ️  Cliente ya existía: {cliente}")
        
        print(f"    Teléfono: {cliente.telefono}")
        print(f"    Dirección: {cliente.direccion}")
        
        # Probar duplicación
        print("\n🔄 Probando prevención de duplicados...")
        form2 = RegistroForm(data=form_data)
        
        if not form2.is_valid():
            print("✅ Formulario rechaza duplicados correctamente")
            for field, errors in form2.errors.items():
                print(f"    {field}: {errors}")
        else:
            print("⚠️  Formulario permitió duplicado")
        
    else:
        print("❌ Formulario inválido")
        for field, errors in form.errors.items():
            print(f"    {field}: {errors}")
    
    # Limpiar
    print("\n🧹 Limpiando...")
    Usuario.objects.filter(username=form_data['username']).delete()
    print("✅ Limpieza completada")

def verificar_usuario_existente():
    """Verificar si el usuario oscar_ibañez ya tiene cliente"""
    print("\n=== VERIFICACIÓN USUARIO EXISTENTE ===\n")
    
    try:
        usuario = Usuario.objects.get(username='oscar_ibañez')
        print(f"✅ Usuario encontrado: {usuario.username}")
        
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            print(f"✅ Cliente asociado: {cliente}")
        except Cliente.DoesNotExist:
            print("❌ Usuario no tiene cliente asociado")
            # Crear cliente si no existe
            cliente = Cliente.objects.create(
                usuario=usuario,
                telefono='',
                direccion=''
            )
            print(f"✅ Cliente creado: {cliente}")
            
    except Usuario.DoesNotExist:
        print("❌ Usuario oscar_ibañez no encontrado")

if __name__ == "__main__":
    test_logica_registro()
    verificar_usuario_existente()
