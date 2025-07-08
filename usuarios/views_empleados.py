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
        try:
            # Crear usuario básico
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password1')
            rol = request.POST.get('rol', 'empleado')
            
            # Verificar que el username no exista
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, f'Ya existe un usuario con el nombre "{username}"')
                return render(request, 'usuarios/crear_empleado.html')
            
            # Crear el usuario
            empleado = Usuario.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                rol=rol,
                is_staff=True if rol in ['admin', 'empleado'] else False
            )
            
            messages.success(request, f'Empleado "{empleado.get_full_name()}" creado exitosamente')
            return redirect('usuarios:lista_empleados')
            
        except Exception as e:
            messages.error(request, f'Error al crear empleado: {str(e)}')
    
    return render(request, 'usuarios/crear_empleado.html')

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
        try:
            empleado.first_name = request.POST.get('first_name', empleado.first_name)
            empleado.last_name = request.POST.get('last_name', empleado.last_name)
            empleado.email = request.POST.get('email', empleado.email)
            empleado.rol = request.POST.get('rol', empleado.rol)
            empleado.is_active = request.POST.get('is_active') == 'on'
            empleado.is_staff = True if empleado.rol in ['admin', 'empleado'] else False
            
            # Cambiar contraseña si se proporciona
            new_password = request.POST.get('new_password')
            if new_password:
                empleado.set_password(new_password)
            
            empleado.save()
            messages.success(request, f'Empleado "{empleado.get_full_name()}" actualizado exitosamente')
            return redirect('usuarios:lista_empleados')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar empleado: {str(e)}')
    
    context = {
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
