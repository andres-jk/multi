from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, MetodoPago, Cliente, Direccion
from .models_divipola import Departamento, Municipio

class RegistroForm(UserCreationForm):
    telefono = forms.CharField(label='Teléfono', max_length=50)
    direccion = forms.CharField(label='Dirección', max_length=255)

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'direccion', 'telefono', 'password1', 'password2')

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'numero_identidad']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_identidad': forms.TextInput(attrs={'class': 'form-control'}),
        }

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
        fields = ['calle', 'numero', 'complemento', 'departamento', 'municipio', 'codigo_postal', 'principal']
        widgets = {
            'calle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la calle'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartamento, oficina, etc.'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'municipio': forms.Select(attrs={'class': 'form-control', 'disabled': True}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código postal'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
