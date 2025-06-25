from django import template
from usuarios.models import CarritoItem

register = template.Library()

@register.simple_tag(takes_context=True)
def get_carrito_total(context):
    """Retorna el total de items en el carrito del usuario actual"""
    request = context['request']
    if request.user.is_authenticated:
        return CarritoItem.objects.filter(usuario=request.user).count()
    return 0

@register.filter
def calcular_subtotal(item):
    """Calcula el subtotal para un item del carrito"""
    return float(item.producto.precio) * float(item.cantidad) * float(item.meses_renta)

@register.simple_tag(takes_context=True)
def get_carrito_monto_total(context):
    """Calcula el monto total del carrito del usuario actual"""
    request = context['request']
    if request.user.is_authenticated:
        items = CarritoItem.objects.filter(usuario=request.user)
        total = sum(calcular_subtotal(item) for item in items)
        return f"{total:.2f}"
    return "0.00"
