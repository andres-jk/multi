from django import forms
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
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
        
        # Personalizar labels
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        
    def clean_email(self):
        """Validar que el email no esté ya registrado"""
        email = self.cleaned_data.get('email')
        if email and Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este email.")
        return email
        
    def clean_username(self):
        """Validar que el username no esté ya registrado"""
        username = self.cleaned_data.get('username')
        if username and Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este nombre de usuario.")
        return username
        
    def clean_password1(self):
        """Validar que la contraseña sea segura"""
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
            if password1.isdigit():
                raise forms.ValidationError("La contraseña no puede ser solo números.")
            if password1.lower() in ['password', 'contraseña', '12345678', 'qwerty']:
                raise forms.ValidationError("Esta contraseña es demasiado común.")
        return password1
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'cliente'  # Establecer rol por defecto
        if commit:
            user.save()
        return user

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'numero_identidad', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_identidad': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        self.fields['numero_identidad'].required = True

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['calle', 'numero', 'complemento', 'departamento', 'municipio', 'principal']
        widgets = {
            'calle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la calle'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartamento, oficina, etc.'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'municipio': forms.Select(attrs={'class': 'form-control'}),
        }

class MetodoPagoForm(forms.ModelForm):
    tipo = forms.ChoiceField(
        choices=MetodoPago.TIPO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'tipo-pago'
        })
    )
    
    numero_referencia = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de transacción o referencia'
        })
    )
    
    comprobante = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )

    class Meta:
        model = MetodoPago
        fields = ['tipo', 'numero_referencia', 'comprobante']
    
    def clean(self):
        cleaned_data = super().clean()
        
        tipo = cleaned_data.get('tipo')
        numero_referencia = cleaned_data.get('numero_referencia')
        comprobante = cleaned_data.get('comprobante')
        
        if tipo and tipo != 'efectivo':
            if not numero_referencia:
                self.add_error('numero_referencia', 'Este campo es requerido para pagos diferentes a efectivo.')
            if not comprobante:
                self.add_error('comprobante', 'Debe adjuntar un comprobante de pago.')
        
        return cleaned_data

class ClienteAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(max_length=30, required=False, label='Nombres')
    last_name = forms.CharField(max_length=150, required=False, label='Apellidos')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    numero_identidad = forms.CharField(max_length=20, label='Número de Identidad')
    telefono = forms.CharField(max_length=20, required=False, label='Teléfono')
    direccion = forms.CharField(max_length=255, required=False, label='Dirección')

    class Meta:
        model = Cliente
        fields = ['telefono', 'direccion']

class UsuarioAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'numero_identidad', 'rol')

class UsuarioAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = '__all__'

class EmpleadoCreationForm(forms.ModelForm):
    """Formulario para que administradores creen nuevos empleados"""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Ingrese la misma contraseña que arriba, para verificación.'
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'numero_identidad', 'rol',
                 'puede_gestionar_productos', 'puede_gestionar_pedidos', 'puede_gestionar_recibos',
                 'puede_gestionar_clientes', 'puede_ver_reportes', 'puede_gestionar_inventario',
                 'puede_procesar_pagos', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_identidad': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'puede_gestionar_productos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_pedidos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_recibos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_clientes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_ver_reportes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_inventario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_procesar_pagos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero_identidad'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # Filtrar roles para mostrar solo los apropiados para empleados
        self.fields['rol'].choices = [
            ('empleado', 'Empleado'),
            ('recibos_obra', 'Empleado de Recibos de Obra'),
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1 and len(password1) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password1

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmpleadoUpdateForm(forms.ModelForm):
    """Formulario para que administradores editen empleados existentes"""
    
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'numero_identidad', 'rol',
                 'puede_gestionar_productos', 'puede_gestionar_pedidos', 'puede_gestionar_recibos',
                 'puede_gestionar_clientes', 'puede_ver_reportes', 'puede_gestionar_inventario',
                 'puede_procesar_pagos', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_identidad': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'puede_gestionar_productos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_pedidos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_recibos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_clientes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_ver_reportes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_inventario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_procesar_pagos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero_identidad'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # Filtrar roles para mostrar solo los apropiados para empleados
        self.fields['rol'].choices = [
            ('empleado', 'Empleado'),
            ('recibos_obra', 'Empleado de Recibos de Obra'),
        ]


class CambiarPasswordEmpleadoForm(forms.Form):
    """Formulario para que administradores cambien contraseñas de empleados"""
    nueva_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    nueva_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Ingrese la misma contraseña que arriba, para verificación.'
    )

    def clean_nueva_password2(self):
        password1 = self.cleaned_data.get("nueva_password1")
        password2 = self.cleaned_data.get("nueva_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean_nueva_password1(self):
        password1 = self.cleaned_data.get("nueva_password1")
        if password1 and len(password1) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password1
