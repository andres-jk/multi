from django.contrib import admin
from .models import ReciboObra, DetalleReciboObra, EstadoProductoIndividual
from django.utils.html import format_html
from django.urls import reverse

class EstadoProductoIndividualInline(admin.TabularInline):
    model = EstadoProductoIndividual
    extra = 0
    readonly_fields = ('fecha_revision',)
    fields = ('numero_serie', 'estado', 'observaciones', 'revisado_por', 'fecha_revision')

class DetalleReciboObraInline(admin.TabularInline):
    model = DetalleReciboObra
    extra = 1 # Número de formularios extra para añadir detalles
    readonly_fields = ('cantidad_pendiente',)
    fields = ('producto', 'detalle_pedido', 'cantidad_solicitada', 'cantidad_vuelta', 'cantidad_buen_estado', 'cantidad_danados', 'cantidad_inservibles', 'estado', 'cantidad_pendiente')

class ReciboObraAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'cliente', 'producto_info', 'cantidad_info', 'estado_devolucion', 'fecha_entrega', 'acciones_devolucion')
    list_filter = ('fecha_entrega', 'firmado_cliente', 'firmado_empleado')
    search_fields = ('pedido__id_pedido', 'cliente__usuario__first_name', 'cliente__usuario__last_name')
    date_hierarchy = 'fecha_entrega'
    readonly_fields = ('fecha_entrega', 'estado_general', 'informacion_inventario')
    inlines = [DetalleReciboObraInline]
    
    def producto_info(self, obj):
        if obj.producto:
            return f"{obj.producto.nombre}"
        return "Sin producto asignado"
    producto_info.short_description = 'Producto'
    
    def cantidad_info(self, obj):
        if hasattr(obj, 'cantidad_solicitada'):
            pendiente = obj.cantidad_solicitada - obj.cantidad_vuelta
            if pendiente > 0:
                return format_html(
                    '<span style="color: orange;">Solicitada: {} | Devuelta: {} | <strong>Pendiente: {}</strong></span>',
                    obj.cantidad_solicitada, obj.cantidad_vuelta, pendiente
                )
            else:
                return format_html(
                    '<span style="color: green;">Solicitada: {} | Devuelta: {} | ✅ Completo</span>',
                    obj.cantidad_solicitada, obj.cantidad_vuelta
                )
        return "Sin información de cantidad"
    cantidad_info.short_description = 'Estado de Cantidad'
    
    def estado_devolucion(self, obj):
        if hasattr(obj, 'cantidad_solicitada'):
            pendiente = obj.cantidad_solicitada - obj.cantidad_vuelta
            if pendiente > 0:
                return format_html('<span style="color: red; font-weight: bold;">🔄 PENDIENTE</span>')
            else:
                return format_html('<span style="color: green; font-weight: bold;">✅ DEVUELTO</span>')
        return "Sin información"
    estado_devolucion.short_description = 'Estado Devolución'
    
    def acciones_devolucion(self, obj):
        if hasattr(obj, 'cantidad_solicitada'):
            pendiente = obj.cantidad_solicitada - obj.cantidad_vuelta
            if pendiente > 0:
                url = reverse('recibos:registrar_devolucion', args=[obj.id])
                return format_html(
                    '<a href="{}" class="button" style="background: #007cba; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">🔄 Procesar Devolución</a>',
                    url
                )
        return "No requiere acción"
    acciones_devolucion.short_description = 'Acciones'
    
    def informacion_inventario(self, obj):
        if obj.producto:
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
                '<strong>Estado del Inventario de {}:</strong><br>'
                '• Disponible: {}<br>'
                '• En renta: {}<br>'
                '• Reservada: {}<br>'
                '• Total: {}'
                '</div>',
                obj.producto.nombre,
                obj.producto.cantidad_disponible,
                obj.producto.cantidad_en_renta,
                obj.producto.cantidad_reservada,
                obj.producto.cantidad_total()
            )
        return "Sin información de producto"
    informacion_inventario.short_description = 'Información de Inventario'

class DetalleReciboObraAdmin(admin.ModelAdmin):
    list_display = ('recibo_info', 'producto', 'cantidad_info', 'estado_devolucion', 'estado')
    list_filter = ('estado', 'producto')
    search_fields = ('recibo__pedido__id_pedido', 'producto__nombre')
    readonly_fields = ('cantidad_pendiente', 'informacion_inventario')
    inlines = [EstadoProductoIndividualInline]
    
    def recibo_info(self, obj):
        return f"Recibo #{obj.recibo.id} (Pedido #{obj.recibo.pedido.id_pedido})"
    recibo_info.short_description = 'Recibo'
    
    def cantidad_info(self, obj):
        pendiente = obj.cantidad_pendiente
        if pendiente > 0:
            return format_html(
                '<span style="color: orange;">Solicitada: {} | Devuelta: {} | <strong>Pendiente: {}</strong></span>',
                obj.cantidad_solicitada, obj.cantidad_vuelta, pendiente
            )
        else:
            return format_html(
                '<span style="color: green;">Solicitada: {} | Devuelta: {} | ✅ Completo</span>',
                obj.cantidad_solicitada, obj.cantidad_vuelta
            )
    cantidad_info.short_description = 'Estado de Cantidad'
    
    def estado_devolucion(self, obj):
        if obj.cantidad_pendiente > 0:
            return format_html('<span style="color: red; font-weight: bold;">🔄 PENDIENTE</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ DEVUELTO</span>')
    estado_devolucion.short_description = 'Estado Devolución'
    
    def informacion_inventario(self, obj):
        if obj.producto:
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
                '<strong>Estado del Inventario de {}:</strong><br>'
                '• Disponible: {}<br>'
                '• En renta: {}<br>'
                '• Reservada: {}<br>'
                '• Total: {}'
                '</div>',
                obj.producto.nombre,
                obj.producto.cantidad_disponible,
                obj.producto.cantidad_en_renta,
                obj.producto.cantidad_reservada,
                obj.producto.cantidad_total()
            )
        return "Sin información de producto"
    informacion_inventario.short_description = 'Información de Inventario'

class EstadoProductoIndividualAdmin(admin.ModelAdmin):
    list_display = ('detalle_recibo', 'numero_serie', 'estado', 'fecha_revision', 'revisado_por')
    list_filter = ('estado', 'fecha_revision')
    search_fields = ('numero_serie', 'detalle_recibo__producto__nombre', 'detalle_recibo__recibo__pedido__id_pedido')
    readonly_fields = ('fecha_revision',)

admin.site.register(ReciboObra, ReciboObraAdmin)
admin.site.register(DetalleReciboObra, DetalleReciboObraAdmin)
admin.site.register(EstadoProductoIndividual, EstadoProductoIndividualAdmin)
