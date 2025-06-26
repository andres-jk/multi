"""
Decoradores y utilidades para la gestión de permisos de empleados
"""
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def es_administrador(user):
    """Función para verificar si un usuario es administrador"""
    return user.is_authenticated and (user.tiene_permisos_admin() if hasattr(user, 'tiene_permisos_admin') else False)


def requiere_permiso(permiso):
    """
    Decorador que requiere un permiso específico del empleado
    
    Args:
        permiso (str): El nombre del permiso a verificar 
                      ('productos', 'pedidos', 'recibos', 'clientes', 'reportes', 'inventario', 'pagos')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            
            # Los administradores siempre tienen acceso
            if es_administrador(request.user):
                return view_func(request, *args, **kwargs)
            
            # Verificar permiso específico
            permisos = request.user.permisos_empleado()
            if not permisos.get(permiso, False):
                messages.error(request, f'No tienes permisos para acceder a la gestión de {permiso}.')
                return redirect('usuarios:inicio')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_administrador(view_func):
    """
    Decorador que solo permite acceso a administradores
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        if not es_administrador(request.user):
            messages.error(request, 'Solo los administradores pueden acceder a esta sección.')
            return redirect('usuarios:inicio')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def usuario_activo(view_func):
    """
    Decorador que verifica que el usuario esté activo
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        if not request.user.is_active:
            messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
            return redirect('usuarios:logout')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def puede_gestionar_empleados(user):
    """
    Función que verifica si el usuario puede gestionar empleados
    (solo administradores)
    """
    return user.is_authenticated and es_administrador(user)


# Decoradores usando user_passes_test para compatibilidad con Django
admin_required = user_passes_test(es_administrador)
empleados_required = user_passes_test(puede_gestionar_empleados)


def verificar_permisos_modulo(user, modulo):
    """
    Función auxiliar para verificar permisos de un módulo específico
    
    Args:
        user: El usuario a verificar
        modulo (str): El módulo a verificar ('productos', 'pedidos', etc.)
    
    Returns:
        bool: True si el usuario tiene permisos, False en caso contrario
    """
    if not user.is_authenticated:
        return False
    
    # Los administradores siempre tienen acceso
    if es_administrador(user):
        return True
    
    # Verificar el usuario esté activo
    if not user.is_active:
        return False
    
    # Verificar permiso específico
    permisos = user.permisos_empleado()
    return permisos.get(modulo, False)


def obtener_permisos_usuario(user):
    """
    Obtiene una lista de los permisos del usuario para mostrar en templates
    
    Args:
        user: El usuario
        
    Returns:
        dict: Diccionario con los permisos del usuario
    """
    if not user.is_authenticated:
        return {}
    
    if es_administrador(user):
        return {
            'productos': True,
            'pedidos': True,
            'recibos': True,
            'clientes': True,
            'reportes': True,
            'inventario': True,
            'pagos': True,
            'empleados': True,
        }
    
    permisos = user.permisos_empleado()
    permisos['empleados'] = False  # Solo administradores pueden gestionar empleados
    return permisos
