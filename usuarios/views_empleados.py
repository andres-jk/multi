from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Usuario
from .forms import EmpleadoForm

User = get_user_model()

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
    """Vista para crear un nuevo empleado"""
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            try:
                # Crear el usuario
                empleado = form.save(commit=False)
                empleado.is_staff = True if empleado.rol in ['admin', 'empleado'] else False
                empleado.save()
                
                messages.success(request, f'Empleado "{empleado.get_full_name()}" creado exitosamente')
                return redirect('usuarios:lista_empleados')
                
            except Exception as e:
                messages.error(request, f'Error al crear empleado: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EmpleadoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'usuarios/crear_empleado.html', context)

@login_required
@user_passes_test(es_administrador)
def detalle_empleado(request, empleado_id):
    """Vista para ver detalles de un empleado"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    context = {
        'empleado': empleado,
    }
    return render(request, 'usuarios/detalle_empleado.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_empleado(request, empleado_id):
    """Vista para editar un empleado"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            try:
                empleado_actualizado = form.save(commit=False)
                empleado_actualizado.is_staff = True if empleado_actualizado.rol in ['admin', 'empleado'] else False
                empleado_actualizado.save()
                
                messages.success(request, f'Empleado "{empleado_actualizado.get_full_name()}" actualizado exitosamente')
                return redirect('usuarios:lista_empleados')
                
            except Exception as e:
                messages.error(request, f'Error al actualizar empleado: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EmpleadoForm(instance=empleado)
    
    context = {
        'form': form,
        'empleado': empleado,
    }
    return render(request, 'usuarios/editar_empleado.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_empleado(request, empleado_id):
    """Vista para eliminar (desactivar) un empleado"""
    empleado = get_object_or_404(Usuario, id=empleado_id, rol__in=['empleado', 'recibos_obra'])
    
    if request.method == 'POST':
        try:
            empleado.is_active = False
            empleado.save()
            messages.success(request, f'Empleado "{empleado.get_full_name()}" desactivado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al desactivar empleado: {str(e)}')
    
    return redirect('usuarios:lista_empleados')
