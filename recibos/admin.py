from django.contrib import admin
from .models import ReciboObra

class ReciboObraAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'cliente', 'producto', 'cantidad_solicitada', 'cantidad_vuelta', 'fecha_entrega', 'estado')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('pedido__id_pedido', 'cliente__usuario__first_name', 'cliente__usuario__last_name', 'producto__nombre')
    date_hierarchy = 'fecha_entrega'
    readonly_fields = ('fecha_entrega',)

admin.site.register(ReciboObra, ReciboObraAdmin)
