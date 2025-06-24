from django.contrib import admin
from .models import Usuario, Cliente, Direccion, CarritoItem, MetodoPago

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'rol')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('rol', 'is_active')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'meses_renta', 'fecha_agregado')
    list_filter = ('fecha_agregado', 'reservado')
    search_fields = ('usuario__username', 'producto__nombre')
    raw_id_fields = ['usuario', 'producto']
    readonly_fields = ('fecha_agregado',)

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'calle', 'ciudad', 'departamento', 'es_principal')
    list_filter = ('ciudad', 'departamento', 'es_principal')
    search_fields = ('cliente__usuario__username', 'calle', 'ciudad')

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'monto', 'estado', 'fecha_pago')
    list_filter = ('tipo', 'estado', 'fecha_pago')
    search_fields = ('usuario__username', 'numero_referencia')
    readonly_fields = ('fecha_pago',)
    raw_id_fields = ['usuario']
