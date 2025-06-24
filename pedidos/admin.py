from django.contrib import admin
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'cliente', 'fecha', 'estado_pedido_general', 'estado_seguimiento', 'duracion_renta', 'fecha_vencimiento')
    list_filter = ('estado_pedido_general', 'estado_seguimiento', 'fecha')
    search_fields = ('cliente__nombre', 'direccion_entrega')
    fieldsets = (
        ('Información básica', {
            'fields': ('cliente', 'direccion_entrega', 'notas', 'total', 'metodo_pago')
        }),
        ('Estado y seguimiento', {
            'fields': (
                'estado_pedido_general', 
                'estado_seguimiento', 
                'fecha_pago',
                'fecha_aceptacion',
                'fecha_empaque_inicio',
                'fecha_empaque_fin',
                'fecha_salida_entrega',
                'fecha_entrega_estimada',
                'fecha_entrega_real'
            )
        }),
        ('Renta y devolución', {
            'fields': (
                'duracion_renta',
                'fecha_inicio_renta',
                'fecha_vencimiento',
                'fecha_devolucion_programada',
                'fecha_devolucion_real',
                'dias_retraso',
                'cargo_extra_retraso'
            )
        }),
        ('Recordatorios', {
            'fields': (
                'dias_para_recordatorio',
                'ultimo_recordatorio',
                'recordatorios_enviados'
            )
        })
    )
    readonly_fields = ('dias_retraso', 'cargo_extra_retraso', 'recordatorios_enviados')
    inlines = [DetallePedidoInline]

admin.site.register(Pedido, PedidoAdmin)
