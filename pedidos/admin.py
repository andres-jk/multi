from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from .models import Pedido, DetallePedido, DevolucionParcial, ExtensionRenta, EntregaPedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal', 'tiempo_restante_renta', 'estado_tiempo_visual')
    fields = ('producto', 'cantidad', 'dias_renta', 'precio_diario', 'subtotal', 
              'fecha_entrega', 'fecha_devolucion', 'estado', 'tiempo_restante_renta', 'estado_tiempo_visual')

    def tiempo_restante_renta(self, obj):
        """Muestra el tiempo restante de renta para cada detalle"""
        if not obj.pk:
            return "-"
        return obj.get_tiempo_restante_humanizado_detalle()
    tiempo_restante_renta.short_description = "Tiempo Restante"

    def estado_tiempo_visual(self, obj):
        """Muestra el estado del tiempo con colores"""
        if not obj.pk:
            return "-"
        
        estado = obj.get_estado_tiempo_renta_detalle()
        if not estado:
            return format_html('<span style="color: gray;">No iniciado</span>')
        
        colors = {
            'normal': '#28a745',      # Verde
            'vence_pronto': '#ffc107', # Amarillo
            'vence_hoy': '#fd7e14',   # Naranja
            'vencido': '#dc3545'      # Rojo
        }
        
        icons = {
            'normal': '✓',
            'vence_pronto': '⚠',
            'vence_hoy': '🔔',
            'vencido': '❌'
        }
        
        color = colors.get(estado, '#6c757d')
        icon = icons.get(estado, '?')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, estado.replace('_', ' ').title()
        )
    estado_tiempo_visual.short_description = "Estado Tiempo"

class DevolucionParcialInline(admin.TabularInline):
    model = DevolucionParcial
    extra = 0
    readonly_fields = ('fecha_devolucion', 'procesado_por')
    fields = ('cantidad', 'estado', 'fecha_devolucion', 'procesado_por', 'notas')
    
class ExtensionRentaInline(admin.TabularInline):
    model = ExtensionRenta
    extra = 0
    readonly_fields = ('fecha_extension', 'procesado_por')
    fields = ('cantidad', 'dias_adicionales', 'precio_diario', 'fecha_extension', 'procesado_por', 'notas')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    list_display = ('id_pedido', 'cliente', 'fecha', 'estado_pedido_general', 'total', 
                   'tiempo_restante_pago_display', 'tiempo_restante_renta_display', 'estado_tiempo_renta_visual')
    list_filter = ('estado_pedido_general', 'fecha', 'duracion_renta')
    search_fields = ('id_pedido', 'cliente__usuario__username', 'cliente__usuario__first_name')
    readonly_fields = ('fecha_pago', 'tiempo_restante_pago_info', 'tiempo_restante_renta_info', 
                      'fecha_inicio_renta', 'fecha_fin_renta', 'porcentaje_tiempo_transcurrido',
                      'reporte_tiempo_detallado')
    raw_id_fields = ['cliente']
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'fecha', 'estado_pedido_general', 'direccion_entrega', 'notas')
        }),
        ('Información de Pago', {
            'fields': ('fecha_limite_pago', 'fecha_pago', 'metodo_pago', 'ref_pago', 'tiempo_restante_pago_info')
        }),
        ('Información de Renta', {
            'fields': ('duracion_renta', 'fecha_devolucion_programada', 'fecha_inicio_renta', 
                      'fecha_fin_renta', 'tiempo_restante_renta_info', 'porcentaje_tiempo_transcurrido')
        }),
        ('Totales', {
            'fields': ('subtotal', 'iva', 'costo_transporte', 'total')
        }),
        ('Reporte de Tiempo Detallado', {
            'fields': ('reporte_tiempo_detallado',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente__usuario')

    def tiempo_restante_pago_display(self, obj):
        """Muestra el tiempo restante para el pago en la lista"""
        tiempo = obj.get_tiempo_restante_pago()
        if not tiempo:
            if obj.estado_pedido_general == 'pendiente_pago':
                return format_html('<span style="color: red;">Vencido</span>')
            return '-'
        if tiempo.days > 0:
            return f"{tiempo.days}d {tiempo.seconds//3600}h"
        else:
            horas = tiempo.seconds // 3600
            return f"{horas}h {(tiempo.seconds%3600)//60}m"
    tiempo_restante_pago_display.short_description = "Tiempo Pago"

    def tiempo_restante_renta_display(self, obj):
        """Muestra el tiempo restante de renta en la lista"""
        return obj.get_tiempo_restante_renta_humanizado()
    tiempo_restante_renta_display.short_description = "Tiempo Renta"

    def estado_tiempo_renta_visual(self, obj):
        """Muestra el estado del tiempo con colores"""
        estado = obj.get_estado_tiempo_renta()
        if not estado:
            return format_html('<span style="color: gray;">-</span>')
        
        colors = {
            'normal': '#28a745',      # Verde
            'vence_pronto': '#ffc107', # Amarillo
            'vence_hoy': '#fd7e14',   # Naranja
            'vencido': '#dc3545'      # Rojo
        }
        
        icons = {
            'normal': '✓',
            'vence_pronto': '⚠',
            'vence_hoy': '🔔',
            'vencido': '❌'
        }
        
        color = colors.get(estado, '#6c757d')
        icon = icons.get(estado, '?')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, estado.replace('_', ' ').title()
        )
    estado_tiempo_renta_visual.short_description = "Estado"

    def tiempo_restante_pago_info(self, obj):
        """Información detallada del tiempo de pago"""
        if obj.estado_pedido_general != 'pendiente_pago':
            if obj.fecha_pago:
                return format_html(
                    '<div style="padding: 10px; background-color: #d4edda; border-radius: 5px;">'
                    '<strong>✅ Pagado:</strong> {}<br>'
                    '<strong>Método:</strong> {}'
                    '</div>',
                    obj.fecha_pago.strftime('%d/%m/%Y %H:%M'),
                    obj.metodo_pago or 'No especificado'
                )
            else:
                return format_html('<span style="color: gray;">No aplica para este estado</span>')
        
        tiempo = obj.get_tiempo_restante_pago()
        if not tiempo:
            return format_html(
                '<div style="padding: 10px; background-color: #f8d7da; border-radius: 5px;">'
                '<strong>❌ Pago Vencido</strong><br>'
                '<strong>Límite:</strong> {}'
                '</div>',
                obj.fecha_limite_pago.strftime('%d/%m/%Y %H:%M')
            )
        
        color = '#fff3cd' if tiempo.days <= 0 else '#d1ecf1'
        return format_html(
            '<div style="padding: 10px; background-color: {}; border-radius: 5px;">'
            '<strong>⏰ Tiempo restante:</strong> {}<br>'
            '<strong>Límite:</strong> {}'
            '</div>',
            color,
            obj.get_tiempo_restante_renta_humanizado() if tiempo else 'Vencido',
            obj.fecha_limite_pago.strftime('%d/%m/%Y %H:%M')
        )
    tiempo_restante_pago_info.short_description = "Información de Pago"

    def tiempo_restante_renta_info(self, obj):
        """Información detallada del tiempo de renta"""
        estado = obj.get_estado_tiempo_renta()
        if not estado:
            return format_html('<span style="color: gray;">Renta no iniciada</span>')
        
        colors = {
            'normal': '#d4edda',      # Verde claro
            'vence_pronto': '#fff3cd', # Amarillo claro
            'vence_hoy': '#ffeaa7',   # Naranja claro
            'vencido': '#f8d7da'      # Rojo claro
        }
        
        color = colors.get(estado, '#e9ecef')
        tiempo_humanizado = obj.get_tiempo_restante_renta_humanizado()
        porcentaje = obj.get_porcentaje_tiempo_transcurrido()
        
        return format_html(
            '<div style="padding: 10px; background-color: {}; border-radius: 5px;">'
            '<strong>⏱️ Tiempo restante:</strong> {}<br>'
            '<strong>📊 Progreso:</strong> {:.1f}% completado<br>'
            '<strong>📅 Estado:</strong> {}'
            '</div>',
            color,
            tiempo_humanizado,
            porcentaje,
            estado.replace('_', ' ').title()
        )
    tiempo_restante_renta_info.short_description = "Información de Renta"

    def fecha_inicio_renta(self, obj):
        """Muestra la fecha de inicio de renta"""
        fecha = obj.get_fecha_inicio_renta()
        return fecha.strftime('%d/%m/%Y %H:%M') if fecha else 'No iniciado'
    fecha_inicio_renta.short_description = "Inicio de Renta"

    def fecha_fin_renta(self, obj):
        """Muestra la fecha de fin de renta"""
        fecha = obj.get_fecha_fin_renta()
        return fecha.strftime('%d/%m/%Y %H:%M') if fecha else 'No calculado'
    fecha_fin_renta.short_description = "Fin de Renta"

    def porcentaje_tiempo_transcurrido(self, obj):
        """Muestra el porcentaje de tiempo transcurrido con barra visual"""
        porcentaje = obj.get_porcentaje_tiempo_transcurrido()
        
        # Determinar color de la barra según el porcentaje
        if porcentaje < 50:
            color = '#28a745'  # Verde
        elif porcentaje < 80:
            color = '#ffc107'  # Amarillo
        else:
            color = '#dc3545'  # Rojo
        
        return format_html(
            '<div style="width: 200px; background-color: #e9ecef; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; height: 20px; background-color: {}; text-align: center; line-height: 20px; color: white; font-size: 12px; font-weight: bold;">'        
            '{:.1f}%'
            '</div>'
            '</div>',
            porcentaje, color, porcentaje
        )
    porcentaje_tiempo_transcurrido.short_description = "Progreso Tiempo"

    def reporte_tiempo_detallado(self, obj):
        """Genera un reporte detallado del tiempo de todos los productos"""
        if not obj.pk:
            return "Guarde el pedido primero"
            
        html = ['<div style="font-family: Arial, sans-serif;">']
        html.append('<h3 style="color: #495057; margin-bottom: 15px;">📋 Reporte de Tiempo por Producto</h3>')
        
        # Información general del pedido
        html.append('<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">')
        html.append(f'<h4 style="margin-top: 0; color: #495057;">Pedido #{obj.id_pedido}</h4>')
        html.append(f'<p><strong>Cliente:</strong> {obj.cliente}</p>')
        html.append(f'<p><strong>Estado:</strong> {obj.get_estado_pedido_general_display()}</p>')
        
        if obj.get_fecha_inicio_renta():
            html.append(f'<p><strong>Inicio de renta:</strong> {obj.get_fecha_inicio_renta().strftime("%d/%m/%Y %H:%M")}</p>')
        if obj.get_fecha_fin_renta():
            html.append(f'<p><strong>Fin de renta:</strong> {obj.get_fecha_fin_renta().strftime("%d/%m/%Y %H:%M")}</p>')

        html.append(f'<p><strong>Tiempo restante general:</strong> {obj.get_tiempo_restante_renta_humanizado()}</p>')
        html.append('</div>')
        
        # Detalles por producto
        detalles = obj.detalles.all()
        if detalles:
            html.append('<table style="width: 100%; border-collapse: collapse; margin-top: 15px;">')
            html.append('<thead style="background-color: #e9ecef;">')
            html.append('<tr>')
            html.append('<th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Producto</th>')
            html.append('<th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Cantidad</th>')
            html.append('<th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Días Renta</th>')
            html.append('<th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Fecha Entrega</th>')
            html.append('<th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Tiempo Restante</th>')
            html.append('<th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Estado</th>')
            html.append('</tr>')
            html.append('</thead>')
            html.append('<tbody>')
            
            for detalle in detalles:
                estado_tiempo = detalle.get_estado_tiempo_renta_detalle()
                # Colores según el estado
                row_colors = {
                    'normal': '#d4edda',
                    'vence_pronto': '#fff3cd',
                    'vence_hoy': '#ffeaa7',
                    'vencido': '#f8d7da'
                }
                row_color = row_colors.get(estado_tiempo, '#ffffff')
                
                html.append(f'<tr style="background-color: {row_color};">')
                html.append(f'<td style="padding: 8px; border: 1px solid #dee2e6;">{detalle.producto.nombre}</td>')
                html.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{detalle.cantidad}</td>')
                html.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{detalle.dias_renta}</td>')
                
                fecha_entrega = detalle.fecha_entrega.strftime('%d/%m/%Y') if detalle.fecha_entrega else 'No entregado'
                html.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{fecha_entrega}</td>')
                
                tiempo_restante = detalle.get_tiempo_restante_humanizado_detalle()
                html.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{tiempo_restante}</td>')
                
                estado_display = estado_tiempo.replace('_', ' ').title() if estado_tiempo else 'No iniciado'
                html.append(f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: center;">{estado_display}</td>')
                
                html.append('</tr>')
            
            html.append('</tbody>')
            html.append('</table>')
        else:
            html.append('<p style="color: #6c757d; font-style: italic;">No hay detalles de productos en este pedido.</p>')
        
        # Recomendaciones
        html.append('<div style="background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 20px;">')
        html.append('<h4 style="margin-top: 0; color: #0c5460;">💡 Recomendaciones</h4>')
        
        if obj.debe_notificar_vencimiento():
            html.append('<p style="color: #721c24; font-weight: bold;">⚠️ Este pedido requiere atención inmediata por vencimiento próximo o actual.</p>')
        
        vencidos = [d for d in detalles if d.get_estado_tiempo_renta_detalle() == 'vencido']
        if vencidos:
            html.append(f'<p>📌 {len(vencidos)} producto(s) con renta vencida. Contactar al cliente para devolución.</p>')
        
        pronto_vencimiento = [d for d in detalles if d.get_estado_tiempo_renta_detalle() in ['vence_hoy', 'vence_pronto']]
        if pronto_vencimiento:
            html.append(f'<p>🔔 {len(pronto_vencimiento)} producto(s) próximos a vencer. Enviar recordatorio al cliente.</p>')
        
        html.append('</div>')
        
        html.append('</div>')
        
        return mark_safe(''.join(html))
    reporte_tiempo_detallado.short_description = "Reporte Detallado"

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    list_display = ('pedido', 'producto', 'cantidad', 'dias_renta', 'precio_diario', 'subtotal', 
                   'estado', 'tiempo_restante_display', 'estado_tiempo_visual')
    list_filter = ('estado', 'dias_renta', 'fecha_entrega')
    search_fields = ('pedido__id_pedido', 'producto__nombre')
    raw_id_fields = ['pedido', 'producto']
    readonly_fields = ('subtotal', 'tiempo_restante_info', 'fecha_fin_calculada')
    inlines = [DevolucionParcialInline, ExtensionRentaInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pedido', 'producto')
    
    def tiempo_restante_display(self, obj):
        """Muestra el tiempo restante en la lista"""
        return obj.get_tiempo_restante_humanizado_detalle()
    tiempo_restante_display.short_description = "Tiempo Restante"
    
    def estado_tiempo_visual(self, obj):
        """Muestra el estado del tiempo con colores"""
        estado = obj.get_estado_tiempo_renta_detalle()
        if not estado:
            return format_html('<span style="color: gray;">No iniciado</span>')
        
        colors = {
            'normal': '#28a745',
            'vence_pronto': '#ffc107',
            'vence_hoy': '#fd7e14',
            'vencido': '#dc3545'
        }
        
        icons = {
            'normal': '✓',
            'vence_pronto': '⚠',
            'vence_hoy': '🔔',
            'vencido': '❌'
        }
        
        color = colors.get(estado, '#6c757d')
        icon = icons.get(estado, '?')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, estado.replace('_', ' ').title()
        )
    estado_tiempo_visual.short_description = "Estado Tiempo"
    
    def tiempo_restante_info(self, obj):
        """Información detallada del tiempo restante"""
        estado = obj.get_estado_tiempo_renta_detalle()
        if not estado:
            return format_html('<span style="color: gray;">Producto no entregado aún</span>')
        
        colors = {
            'normal': '#d4edda',
            'vence_pronto': '#fff3cd',
            'vence_hoy': '#ffeaa7',
            'vencido': '#f8d7da'
        }
        
        color = colors.get(estado, '#e9ecef')
        tiempo_humanizado = obj.get_tiempo_restante_humanizado_detalle()
        
        info_html = f'''
        <div style="padding: 10px; background-color: {color}; border-radius: 5px;">
            <strong>⏱️ Tiempo restante:</strong> {tiempo_humanizado}<br>
        '''
        
        if obj.fecha_entrega:
            info_html += f'<strong>📅 Entregado:</strong> {obj.fecha_entrega.strftime("%d/%m/%Y %H:%M")}<br>'
        
        if obj.get_fecha_fin_renta_detalle():
            info_html += f'<strong>📅 Debe devolver:</strong> {obj.get_fecha_fin_renta_detalle().strftime("%d/%m/%Y %H:%M")}<br>'
        
        info_html += f'<strong>📊 Estado:</strong> {estado.replace("_", " ").title()}'
        info_html += '</div>'
        
        return format_html(info_html)
    tiempo_restante_info.short_description = "Información de Tiempo"
    
    def fecha_fin_calculada(self, obj):
        """Muestra la fecha calculada de fin de renta"""
        fecha = obj.get_fecha_fin_renta_detalle()
        return fecha.strftime('%d/%m/%Y %H:%M') if fecha else 'No calculado'
    fecha_fin_calculada.short_description = "Fecha Fin Renta"

@admin.register(EntregaPedido)
class EntregaPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'empleado_entrega', 'estado_entrega', 'fecha_programada', 'vehiculo_placa']
    list_filter = ['estado_entrega', 'fecha_programada', 'empleado_entrega']
    search_fields = ['pedido__id_pedido', 'vehiculo_placa', 'conductor_nombre']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('pedido', 'empleado_entrega', 'estado_entrega')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'fecha_inicio_recorrido', 'fecha_entrega_real')
        }),
        ('Ubicaciones', {
            'fields': ('direccion_salida', 'direccion_destino')
        }),
        ('Vehículo', {
            'fields': ('vehiculo_placa', 'conductor_nombre', 'conductor_telefono')
        }),
        ('GPS y Seguimiento', {
            'fields': ('latitud_actual', 'longitud_actual', 'ultima_actualizacion_gps', 'tiempo_estimado_llegada', 'distancia_restante_km'),
            'classes': ('collapse',)
        }),
        ('Adicional', {
            'fields': ('observaciones', 'firma_recepcion', 'foto_entrega'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(DevolucionParcial)
class DevolucionParcialAdmin(admin.ModelAdmin):
    list_display = ('id', 'detalle_pedido', 'cantidad', 'estado', 'fecha_devolucion', 'procesado_por')
    list_filter = ('estado', 'fecha_devolucion')
    search_fields = ('detalle_pedido__producto__nombre', 'notas')
    date_hierarchy = 'fecha_devolucion'
    
    def get_pedido(self, obj):
        return obj.detalle_pedido.pedido.id_pedido
    get_pedido.short_description = 'Pedido'

@admin.register(ExtensionRenta)
class ExtensionRentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'detalle_pedido', 'cantidad', 'dias_adicionales', 'subtotal', 'fecha_extension', 'procesado_por')
    list_filter = ('fecha_extension',)
    search_fields = ('detalle_pedido__producto__nombre', 'notas')
    date_hierarchy = 'fecha_extension'
    
    def get_pedido(self, obj):
        return obj.detalle_pedido.pedido.id_pedido
    get_pedido.short_description = 'Pedido'
