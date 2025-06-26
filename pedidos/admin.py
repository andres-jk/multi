from django.contrib import admin
from .models import Pedido, DetallePedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'cliente', 'fecha', 'estado_pedido_general', 'total')
    list_filter = ('estado_pedido_general', 'fecha')
    search_fields = ('id_pedido', 'cliente__usuario__username', 'cliente__usuario__first_name')
    readonly_fields = ('fecha_pago',)
    raw_id_fields = ['cliente']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente__usuario')

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pe)ido', 'producto', 'cantidad', 'meses_renta', 'precio_unitario', 'subtotal')
    list_filter = ('estado', 'meses_renta')
    search_fields = ('pedido__id_pedido', 'producto__nombre')
    raw_id_fields = ['pedido', 'producto']
    readonly_fields = ('subtotal',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pedido', 'producto')
