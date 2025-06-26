from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'tipo_renta', 
        'precio', 
        'precio_semanal', 
        'peso',
        'cantidad_disponible', 
        'activo'
    ]
    list_filter = ['tipo_renta', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'imagen', 'activo')
        }),
        ('Precios y Tipo de Renta', {
            'fields': ('tipo_renta', 'precio', 'precio_semanal', 'peso'),
            'description': 'Configure el tipo de renta, precios y peso del producto. Si no especifica precio semanal, se calculará automáticamente como precio mensual ÷ 4.'
        }),
        ('Inventario', {
            'fields': ('cantidad_disponible', 'cantidad_reservada', 'cantidad_en_renta'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['cantidad_reservada', 'cantidad_en_renta']
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado para calcular precio semanal automáticamente"""
        super().save_model(request, obj, form, change)
        
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
