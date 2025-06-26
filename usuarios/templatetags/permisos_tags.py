"""
Template tags para la gestión de permisos de empleados
"""
from django import template
from django.contrib.auth.models import AnonymousUser
from ..decorators import verificar_permisos_modulo, es_administrador, obtener_permisos_usuario

register = template.Library()


@register.filter
def tiene_permiso(user, modulo):
    """
    Verifica si el usuario tiene permiso para un módulo específico
    
    Uso en template:
    {% if user|tiene_permiso:"productos" %}
        <!-- Contenido para usuarios con permiso de productos -->
    {% endif %}
    """
    if isinstance(user, AnonymousUser):
        return False
    return verificar_permisos_modulo(user, modulo)


@register.filter
def es_admin(user):
    """
    Verifica si el usuario es administrador
    
    Uso en template:
    {% if user|es_admin %}
        <!-- Contenido solo para administradores -->
    {% endif %}
    """
    if isinstance(user, AnonymousUser):
        return False
    return es_administrador(user)


@register.simple_tag
def permisos_usuario(user):
    """
    Obtiene todos los permisos del usuario
    
    Uso en template:
    {% permisos_usuario user as permisos %}
    {% if permisos.productos %}
        <!-- Usuario puede gestionar productos -->
    {% endif %}
    """
    if isinstance(user, AnonymousUser):
        return {}
    return obtener_permisos_usuario(user)


@register.inclusion_tag('usuarios/permisos_badge.html')
def mostrar_permisos(user):
    """
    Muestra los permisos del usuario en forma de badges
    
    Uso en template:
    {% mostrar_permisos user %}
    """
    if isinstance(user, AnonymousUser):
        return {'permisos': {}, 'es_admin': False}
    
    return {
        'permisos': obtener_permisos_usuario(user),
        'es_admin': es_administrador(user),
        'user': user
    }


@register.simple_tag
def puede_acceder(user, modulo):
    """
    Verifica si el usuario puede acceder a un módulo
    Retorna True/False para uso en condiciones
    
    Uso en template:
    {% puede_acceder user "productos" as puede_productos %}
    {% if puede_productos %}
        <!-- Contenido -->
    {% endif %}
    """
    if isinstance(user, AnonymousUser):
        return False
    return verificar_permisos_modulo(user, modulo)


@register.filter
def get_rol_display(user):
    """
    Obtiene el nombre del rol del usuario para mostrar
    
    Uso en template:
    {{ user|get_rol_display }}
    """
    if isinstance(user, AnonymousUser):
        return "Usuario anónimo"
    
    if hasattr(user, 'get_rol_display'):
        return user.get_rol_display()
    return "Sin rol definido"
