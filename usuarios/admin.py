from django.contrib import admin
from django.utils import timezone
from .models import Usuario, Cliente, Direccion, CarritoItem, MetodoPago
from .models_divipola import Departamento, Municipio
from .utils import enviar_correo_pago

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
    list_display = ('usuario', 'calle', 'municipio', 'departamento', 'principal')
    list_filter = ('departamento', 'municipio', 'principal')
    search_fields = ('usuario__username', 'calle', 'municipio__nombre', 'departamento__nombre')
    raw_id_fields = ['usuario', 'departamento', 'municipio']

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'tipo', 'usuario', 'monto', 'estado', 'fecha_pago', 'fecha_verificacion', 'dias_pendiente')
    list_filter = ('tipo', 'estado', 'fecha_pago', 'fecha_verificacion')
    search_fields = ('usuario__username', 'pedido__id_pedido', 'numero_referencia')
    readonly_fields = ('fecha_creacion', 'fecha_pago', 'fecha_verificacion')
    raw_id_fields = ['usuario', 'pedido', 'verificado_por']
    actions = ['aprobar_pagos', 'rechazar_pagos']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('pedido', 'usuario', 'tipo', 'monto', 'estado')
        }),
        ('Detalles del Pago', {
            'fields': ('comprobante', 'numero_referencia', 'notas')
        }),
        ('Información de Verificación', {
            'fields': ('verificado_por', 'fecha_verificacion', 'fecha_pago', 'fecha_creacion')
        })
    )

    def dias_pendiente(self, obj):
        if obj.estado == 'pendiente' and not obj.fecha_verificacion:
            return (timezone.now() - obj.fecha_creacion).days
        return '-'
    dias_pendiente.short_description = 'Días Pendiente'

    def aprobar_pagos(self, request, queryset):
        for pago in queryset.filter(estado='pendiente'):
            pago.estado = 'aprobado'
            pago.verificado_por = request.user
            pago.fecha_verificacion = timezone.now()
            pago.fecha_pago = timezone.now()
            pago.save()
            
            # Enviar correo de confirmación
            enviar_correo_pago(pago.pedido, 'aprobado')
            
        self.message_user(request, f'Se aprobaron {queryset.count()} pagos exitosamente.')
    aprobar_pagos.short_description = 'Aprobar pagos seleccionados'

    def rechazar_pagos(self, request, queryset):
        for pago in queryset.filter(estado='pendiente'):
            pago.estado = 'rechazado'
            pago.verificado_por = request.user
            pago.fecha_verificacion = timezone.now()
            pago.save()
            
            # Enviar correo de rechazo
            enviar_correo_pago(pago.pedido, 'rechazado')
            
        self.message_user(request, f'Se rechazaron {queryset.count()} pagos.')
    rechazar_pagos.short_description = 'Rechazar pagos seleccionados'

    def save_model(self, request, obj, form, change):
        if 'estado' in form.changed_data:
            obj.verificado_por = request.user
            obj.fecha_verificacion = timezone.now()
            if obj.estado == 'aprobado':
                obj.fecha_pago = timezone.now()
                # Enviar correo de confirmación
                enviar_correo_pago(obj.pedido, 'aprobado')
            elif obj.estado == 'rechazado':
                # Enviar correo de rechazo
                enviar_correo_pago(obj.pedido, 'rechazado')
        super().save_model(request, obj, form, change)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')
    ordering = ('nombre',)

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento', 'codigo', 'costo_transporte')
    list_filter = ('departamento',)
    search_fields = ('nombre', 'codigo', 'departamento__nombre')
    raw_id_fields = ['departamento']
    list_editable = ['costo_transporte']
