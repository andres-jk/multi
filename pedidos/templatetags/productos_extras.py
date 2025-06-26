from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def div(value, arg):
    """Divide el valor por el argumento"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def currency(value):
    """Formatea un número como moneda"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def precio_calculado(value):
    """Calcula el precio semanal como 1/4 del mensual"""
    try:
        return float(value) / 4
    except (ValueError, TypeError):
        return 0
