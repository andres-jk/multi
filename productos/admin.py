from django.contrib import admin
from django.utils.html import format_html
from .models import Producto
from .forms import ProductoAdminForm

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm
    
    class Media:
        js = ('admin/js/producto_admin.js',)
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    list_display = [
        'nombre', 
        'precio_display', 
        'dias_minimos_renta',
        'peso',
        'cantidad_disponible', 
        'activo'
    ]
    list_filter = ['dias_minimos_renta', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'imagen', 'activo')
        }),
        ('Precios y Renta', {
            'fields': ('precio_diario', 'dias_minimos_renta', 'peso'),
            'description': 'Configure el precio diario y los días mínimos de renta.'
        }),
        ('Inventario', {
            'fields': ('cantidad_disponible', 'cantidad_reservada', 'cantidad_en_renta'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['cantidad_reservada', 'cantidad_en_renta']
    
    def precio_display(self, obj):
        """Mostrar el precio formateado"""
        return obj.get_precio_display()
    precio_display.short_description = 'Precio'
