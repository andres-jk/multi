#!/usr/bin/env python
"""
Script final para verificar que el formulario de registro está completamente corregido
"""
import os
import sys

sys.path.append(r'c:\Users\andre\OneDrive\Documentos\MultiAndamios')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiandamios.settings")

import django
django.setup()

from django.test import Client
from usuarios.models import Usuario, Cliente
from usuarios.forms import RegistroForm

def test_todos_los_casos():
    """Probar todos los casos posibles del formulario"""
    print("=== TEST COMPLETO DEL FORMULARIO DE REGISTRO ===\n")
    
    test_cases = [
        {
            'name': '✅ Registro válido completo',
            'data': {
                'username': 'usuario_completo',
                'first_name': 'Usuario',
                'last_name': 'Completo',
                'email': 'completo@test.com',
                'telefono': '3001234567',
                'direccion': 'Calle 123 # 45-67',
                'password1': 'ContraseñaSegura123',
                'password2': 'ContraseñaSegura123',
            },
            'should_pass': True
        },
        {
            'name': '✅ Registro mínimo válido',
            'data': {
                'username': 'usuario_minimo',
                'password1': 'ContraseñaSegura123',
                'password2': 'ContraseñaSegura123',
            },
            'should_pass': True
        },
        {
            'name': '❌ Contraseñas no coinciden',
            'data': {
                'username': 'usuario_pass_diff',
                'password1': 'Contraseña123',
                'password2': 'Contraseña456',
            },
            'should_pass': False,
            'expected_error': 'password2'
        },
        {
            'name': '❌ Contraseña muy corta',
            'data': {
                'username': 'usuario_pass_corta',
                'password1': '123',
                'password2': '123',
            },
            'should_pass': False,
            'expected_error': 'password1'
        },
        {
            'name': '❌ Email inválido',
            'data': {
                'username': 'usuario_email_mal',
                'email': 'email_invalido',
                'password1': 'ContraseñaSegura123',
                'password2': 'ContraseñaSegura123',
            },
            'should_pass': False,
            'expected_error': 'email'
        },
        {
            'name': '❌ Username vacío',
            'data': {
                'username': '',
                'password1': 'ContraseñaSegura123',
                'password2': 'ContraseñaSegura123',
            },
            'should_pass': False,
            'expected_error': 'username'
        },
        {
            'name': '❌ Contraseña común',
            'data': {
                'username': 'usuario_pass_comun',
                'password1': 'password',
                'password2': 'password',
            },
            'should_pass': False,
            'expected_error': 'password1'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        
        # Limpiar usuario si existe
        username = test_case['data'].get('username')
        if username:
            Usuario.objects.filter(username=username).delete()
        
        form = RegistroForm(data=test_case['data'])
        
        if test_case['should_pass']:
            if form.is_valid():
                print("   ✅ Formulario válido (como esperado)")
                try:
                    usuario = form.save()
                    print(f"   ✅ Usuario creado: {usuario.username}")
                    
                    # Verificar que se puede crear cliente
                    cliente, created = Cliente.objects.get_or_create(
                        usuario=usuario,
                        defaults={
                            'telefono': form.cleaned_data.get('telefono', ''),
                            'direccion': form.cleaned_data.get('direccion', '')
                        }
                    )
                    print(f"   ✅ Cliente {'creado' if created else 'existente'}: {cliente}")
                    
                    # Limpiar
                    usuario.delete()
                    
                except Exception as e:
                    print(f"   ❌ Error al guardar: {e}")
            else:
                print("   ❌ Formulario inválido (inesperado)")
                for field, errors in form.errors.items():
                    print(f"      {field}: {', '.join(errors)}")
        else:
            if not form.is_valid():
                print("   ✅ Formulario inválido (como esperado)")
                expected_field = test_case.get('expected_error')
                if expected_field and expected_field in form.errors:
                    print(f"   ✅ Error en campo esperado ({expected_field})")
                elif expected_field:
                    print(f"   ⚠️  Error esperado en {expected_field}, pero errores en: {list(form.errors.keys())}")
                
                # Mostrar errores
                for field, errors in form.errors.items():
                    print(f"      {field}: {', '.join(errors)}")
            else:
                print("   ❌ Formulario válido (inesperado)")
        
        print()

def test_duplicacion():
    """Probar prevención de duplicación"""
    print("=== TEST DE PREVENCIÓN DE DUPLICACIÓN ===\n")
    
    # Crear usuario base
    base_data = {
        'username': 'usuario_duplicacion',
        'email': 'duplicacion@test.com',
        'password1': 'ContraseñaSegura123',
        'password2': 'ContraseñaSegura123',
    }
    
    print("1. Creando usuario inicial...")
    Usuario.objects.filter(username=base_data['username']).delete()
    Usuario.objects.filter(email=base_data['email']).delete()
    
    form1 = RegistroForm(data=base_data)
    if form1.is_valid():
        usuario1 = form1.save()
        print(f"   ✅ Usuario creado: {usuario1.username}")
        
        # Intentar crear duplicado por username
        print("2. Intentando duplicar username...")
        form2 = RegistroForm(data={
            'username': 'usuario_duplicacion',  # Mismo username
            'email': 'otro@test.com',
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        })
        
        if not form2.is_valid() and 'username' in form2.errors:
            print("   ✅ Duplicación de username bloqueada correctamente")
        else:
            print("   ❌ Duplicación de username NO fue bloqueada")
        
        # Intentar crear duplicado por email
        print("3. Intentando duplicar email...")
        form3 = RegistroForm(data={
            'username': 'otro_usuario',
            'email': 'duplicacion@test.com',  # Mismo email
            'password1': 'ContraseñaSegura123',
            'password2': 'ContraseñaSegura123',
        })
        
        if not form3.is_valid() and 'email' in form3.errors:
            print("   ✅ Duplicación de email bloqueada correctamente")
        else:
            print("   ❌ Duplicación de email NO fue bloqueada")
        
        # Limpiar
        usuario1.delete()
        
    else:
        print("   ❌ No se pudo crear usuario inicial")
        for field, errors in form1.errors.items():
            print(f"      {field}: {', '.join(errors)}")

if __name__ == "__main__":
    test_todos_los_casos()
    print("\n" + "="*60 + "\n")
    test_duplicacion()
    print("\n✅ TODOS LOS TESTS COMPLETADOS")
