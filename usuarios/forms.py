from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, MetodoPago, Cliente, Direccion
from .models_divipola import Departamento, Municipio

class RegistroForm(UserCreationForm):
    direccion_texto = forms.CharField(
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
        fields = ['first_name', 'last_name', 'email', 'direccion_texto']
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
            'direccion_texto': forms.TextInput(attrs={
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
        fields = ['telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
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
        fields = ['calle', 'numero', 'complemento', 'departamento', 'municipio', 'codigo_postal', 'principal']
        widgets = {
            'calle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la calle'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartamento, oficina, etc.'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
        fields = ['tipo', 'monto', 'numero_referencia', 'comprobante', 'notas']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monto del pago',
                'step': '0.01'
            }),
            'numero_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia o transacción'
            }),
            'comprobante': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales',
                'rows': 3
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
        fields = ['username', 'first_name', 'last_name', 'email', 'direccion_texto', 'rol', 'is_staff', 'is_active']
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
            'direccion_texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección del empleado'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-control'
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
            'direccion_texto': 'Dirección',
            'rol': 'Rol del empleado',
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

# Formularios para el admin de Django
class UsuarioAdminCreationForm(UserCreationForm):
    """Formulario para crear usuarios en el admin de Django."""

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff', 'is_active')


class UsuarioAdminChangeForm(UserChangeForm):
    """Formulario para editar usuarios en el admin de Django."""

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'direccion_texto', 'rol', 
                 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions',
                 'puede_gestionar_productos', 'puede_gestionar_pedidos', 'puede_gestionar_recibos',
                 'puede_gestionar_clientes', 'puede_ver_reportes', 'puede_gestionar_inventario',
                 'puede_procesar_pagos', 'activo', 'last_login', 'date_joined')

class ClienteCompletoForm(forms.Form):
    """Formulario para crear un cliente completo desde el panel admin."""
    
    # Datos del usuario
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    numero_identidad = forms.CharField(
        label='Número de identidad',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Datos del cliente
    telefono = forms.CharField(
        label='Teléfono',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    direccion = forms.CharField(
        label='Dirección',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_numero_identidad(self):
        numero_identidad = self.cleaned_data.get('numero_identidad')
        if numero_identidad and Usuario.objects.filter(numero_identidad=numero_identidad).exists():
            raise forms.ValidationError('Este número de identidad ya está registrado.')
        return numero_identidad
