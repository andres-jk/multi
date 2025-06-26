from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usuario
from .forms import EmpleadoCreationForm, EmpleadoUpdateForm, CambiarPasswordEmpleadoForm

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

@login_required
@user_passes_test(es_administrador)
def crear_empleado(request):
    """Vista para que administradores creen empleados"""
    if request.method == 'POST':
        form = EmpleadoCreationForm(request.POST)
        if form.is_valid():
            try:
                empleado = form.save()
                messages.success(request, f'Empleado {empleado.username} creado exitosamente.')
                return redirect('usuarios:lista_empleados')
            except Exception as e:
                messages.error(request, f'Error al crear empleado: {str(e)}')
    else:
        form = EmpleadoCreationForm()
    
    return render(request, 'usuarios/crear_empleado.html', {'form': form})

@login_required
@user_passes_test(es_administrador)
def editar_empleado(request, empleado_id):
    """Vista para que administradores editen empleados"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    if request.method == 'POST':
        form = EmpleadoUpdateForm(request.POST, instance=empleado)
        if form.is_valid():
            try:
                empleado = form.save()
                messages.success(request, f'Empleado {empleado.username} actualizado exitosamente.')
                return redirect('usuarios:detalle_empleado', empleado_id=empleado.id)
            except Exception as e:
                messages.error(request, f'Error al actualizar empleado: {str(e)}')
    else:
        form = EmpleadoUpdateForm(instance=empleado)
    
    return render(request, 'usuarios/editar_empleado.html', {
        'form': form,
        'empleado': empleado
    })

@login_required
@user_passes_test(es_administrador)
def cambiar_password_empleado(request, empleado_id):
    """Vista para que administradores cambien contraseñas de empleados"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    if request.method == 'POST':
        form = CambiarPasswordEmpleadoForm(request.POST)
        if form.is_valid():
            try:
                nueva_password = form.cleaned_data['nueva_password1']
                empleado.set_password(nueva_password)
                empleado.save()
                messages.success(request, f'Contraseña del empleado {empleado.username} cambiada exitosamente.')
                return redirect('usuarios:lista_empleados')
            except Exception as e:
                messages.error(request, f'Error al cambiar contraseña: {str(e)}')
    else:
        form = CambiarPasswordEmpleadoForm()
    
    return render(request, 'usuarios/cambiar_password_empleado.html', {
        'form': form,
        'empleado': empleado
    })

@login_required
@user_passes_test(es_administrador)
def activar_desactivar_empleado(request, empleado_id):
    """Vista para que administradores activen/desactiven empleados"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    if request.method == 'POST':
        empleado.is_active = not empleado.is_active
        empleado.save()
        
        estado = "activado" if empleado.is_active else "desactivado"
        messages.success(request, f'Empleado {empleado.username} {estado} exitosamente.')
    
    return redirect('usuarios:lista_empleados')

@login_required
@user_passes_test(es_administrador)
def eliminar_empleado(request, empleado_id):
    """Vista para que administradores eliminen empleados"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    if request.method == 'POST':
        username = empleado.username
        empleado.delete()
        messages.success(request, f'Empleado {username} eliminado exitosamente.')
    
    return redirect('usuarios:lista_empleados')

@login_required
@user_passes_test(es_administrador)
def detalle_empleado(request, empleado_id):
    """Vista para que administradores vean detalles de empleados"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    context = {
        'empleado': empleado,
        'permisos': empleado.permisos_empleado() if hasattr(empleado, 'permisos_empleado') else [],
        'fecha_ultimo_login': empleado.last_login,
        'fecha_creacion': empleado.date_joined,
    }
    
    return render(request, 'usuarios/detalle_empleado.html', context)
