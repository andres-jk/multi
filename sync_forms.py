#!/usr/bin/env python3
"""
Script para verificar y sincronizar el archivo usuarios/forms.py
con todas las clases de formularios necesarias.
"""

import os
import sys

def create_complete_forms_file():
    """Crea o reemplaza el archivo usuarios/forms.py con todo el contenido necesario."""
    
    forms_content = '''from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, MetodoPago, Cliente, Direccion
from .models_divipola import Departamento, Municipio

class RegistroForm(UserCreationForm):
    telefono = forms.CharField(
        label='Teléfono', 
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 3001234567'
        })
    )
    direccion = forms.CharField(
        label='Dirección', 
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Carrera 7 # 123-45'
        })
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets para campos de contraseña
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3001234567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Carrera 7 # 123-45'
            }),
        }

class ClienteForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    municipio = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula', 'telefono', 'email', 'direccion', 'departamento', 'municipio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del cliente'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cédula'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'departamento' in self.data:
            try:
                departamento_id = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.municipio:
            self.fields['municipio'].queryset = self.instance.municipio.departamento.municipio_set.all()

class DireccionForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    municipio = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Direccion
        fields = ['nombre', 'direccion', 'departamento', 'municipio', 'telefono', 'es_principal']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Casa, Oficina, etc.'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono opcional'
            }),
            'es_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'departamento' in self.data:
            try:
                departamento_id = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.municipio:
            self.fields['municipio'].queryset = self.instance.municipio.departamento.municipio_set.all()

class MetodoPagoForm(forms.ModelForm):
    class Meta:
        model = MetodoPago
        fields = ['tipo', 'nombre_titular', 'numero_tarjeta', 'fecha_vencimiento', 'codigo_seguridad']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre_titular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre como aparece en la tarjeta'
            }),
            'numero_tarjeta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234 5678 9012 3456',
                'maxlength': '19'
            }),
            'fecha_vencimiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MM/AA',
                'maxlength': '5'
            }),
            'codigo_seguridad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CVV',
                'maxlength': '4'
            }),
        }

class EmpleadoForm(forms.ModelForm):
    """Formulario para crear y editar empleados."""
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Dejar en blanco para mantener la contraseña actual (solo al editar)'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 'is_staff', 'is_active']
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
            'is_active': forms.CheckboxInput(attrs={
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
            'is_active': 'Usuario activo',
        }
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        return user
'''

    forms_file = 'usuarios/forms.py'
    
    try:
        # Crear respaldo del archivo actual si existe
        if os.path.exists(forms_file):
            backup_file = f"{forms_file}.backup"
            with open(forms_file, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Respaldo creado: {backup_file}")
        
        # Escribir el nuevo contenido
        with open(forms_file, 'w', encoding='utf-8') as f:
            f.write(forms_content)
        
        print(f"✅ Archivo {forms_file} actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar el archivo: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Actualizando usuarios/forms.py con todas las clases necesarias...")
    success = create_complete_forms_file()
    
    if success:
        print("\n✅ Actualización completada exitosamente")
        print("📋 El archivo usuarios/forms.py ahora incluye:")
        print("   - RegistroForm")
        print("   - PerfilForm") 
        print("   - ClienteForm")
        print("   - DireccionForm")
        print("   - MetodoPagoForm")
        print("   - EmpleadoForm (con validación de contraseñas)")
        print("\n📋 Próximos pasos:")
        print("1. git add usuarios/forms.py")
        print("2. git commit -m 'Fix: Actualizar forms.py con EmpleadoForm completo'")
        print("3. git push")
        print("4. En PythonAnywhere: git pull && reload web app")
    else:
        print("\n❌ La actualización falló")
        sys.exit(1)
