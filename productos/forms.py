from django import forms
from .models import Producto

class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'precio_diario': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 1500.00'
            }),
            'dias_minimos_renta': forms.NumberInput(attrs={
                'step': '1',
                'min': '1',
                'placeholder': 'Ej: 7'
            }),
        }
        
    def clean_dias_minimos_renta(self):
        dias = self.cleaned_data.get('dias_minimos_renta')
        if dias < 1:
            raise forms.ValidationError('Los días mínimos de renta deben ser al menos 1.')
        return dias
    
    def clean_precio_diario(self):
        precio = self.cleaned_data.get('precio_diario')
        if precio <= 0:
            raise forms.ValidationError('El precio diario debe ser mayor a 0.')
        return precio
