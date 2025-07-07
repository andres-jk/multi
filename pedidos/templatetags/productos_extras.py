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
def calcular_precio_total(precio_diario, dias):
    """Calcula el precio total basado en el precio por día y la cantidad de días"""
    try:
        return float(precio_diario) * float(dias)
    except (ValueError, TypeError):
        return 0

@register.filter
def dias_pluralize(value):
    """Retorna 's' si el valor es diferente a 1, para pluralizar 'día'"""
    try:
        return '' if int(value) == 1 else 's'
    except (ValueError, TypeError):
        return 's'
