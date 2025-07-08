#!/usr/bin/env python3
"""
Script para agregar la clase EmpleadoForm al archivo usuarios/forms.py
si no existe, para solucionar el error de importación en el servidor.
"""

import os
import sys

def fix_empleado_form():
    forms_file = 'usuarios/forms.py'
    
    if not os.path.exists(forms_file):
        print(f"❌ El archivo {forms_file} no existe")
        return False
    
    # Leer el contenido actual
    with open(forms_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya existe EmpleadoForm
    if 'class EmpleadoForm' in content:
        print("✅ La clase EmpleadoForm ya existe en usuarios/forms.py")
        return True
    
    # Código de la clase EmpleadoForm a agregar
    empleado_form_code = '''
class EmpleadoForm(forms.ModelForm):
    """Formulario para crear y editar empleados."""
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del empleado'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del empleado'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@empresa.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección del empleado'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'is_staff': 'Es empleado/administrador',
        }
'''
    
    # Agregar la clase al final del archivo
    content += empleado_form_code
    
    # Escribir el archivo actualizado
    try:
        with open(forms_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Se agregó la clase EmpleadoForm a usuarios/forms.py")
        return True
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Verificando y corrigiendo EmpleadoForm en usuarios/forms.py...")
    success = fix_empleado_form()
    
    if success:
        print("\n✅ Corrección completada exitosamente")
        print("📋 Próximos pasos:")
        print("1. git add usuarios/forms.py")
        print("2. git commit -m 'Fix: Agregar EmpleadoForm faltante'")
        print("3. git push")
        print("4. En PythonAnywhere: git pull && reload web app")
    else:
        print("\n❌ La corrección falló")
        sys.exit(1)
