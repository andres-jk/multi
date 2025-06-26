from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usuario

def es_administrador(user):
    """Función para verificar si un usuario es administrador"""
    return user.is_authenticated and (user.tiene_permisos_admin() if hasattr(user, 'tiene_permisos_admin') else False)

@login_required
@user_passes_test(es_administrador)
def lista_empleados(request):
    """Vista para que administradores vean y gestionen empleados"""
    empleados = Usuario.objects.filter(rol__in=['empleado', 'recibos_obra']).order_by('username')
    
    context = {
        'empleados': empleados,
        'total_empleados': empleados.count(),
        'empleados_activos': empleados.filter(is_active=True).count(),
        'empleados_inactivos': empleados.filter(is_active=False).count(),
    }
    return render(request, 'usuarios/lista_empleados.html', context)
