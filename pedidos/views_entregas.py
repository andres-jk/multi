from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import json
from decimal import Decimal

from .models import Pedido, EntregaPedido, DetallePedido
from usuarios.models import Usuario

def es_empleado_recibos(user):
    """Verifica si el usuario es empleado de recibos de obra"""
    return user.is_authenticated and (user.rol == 'recibos_obra' or user.rol == 'admin')

def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and user.rol == 'admin'

@login_required
@user_passes_test(es_empleado_recibos)
def panel_entregas(request):
    """Panel principal para empleados de recibos de obra"""
    
    # Verificar si se solicita limpiar filtros
    if 'clear' in request.GET:
        if 'entregas_estado_filtro' in request.session:
            del request.session['entregas_estado_filtro']
        if 'entregas_fecha_filtro' in request.session:
            del request.session['entregas_fecha_filtro']
        return redirect('pedidos:panel_entregas')
    
    # Mostrar mensaje informativo para los empleados
    entregas_en_camino = EntregaPedido.objects.filter(estado_entrega='en_camino').count()
    if entregas_en_camino > 0:
        messages.success(request, f"¡Importante! Hay {entregas_en_camino} entregas en camino que se mantendrán visibles en todo momento.")
    else:
        messages.info(request, "Bienvenido al panel de entregas. Ahora todos los empleados de recibos pueden gestionar cualquier entrega programada.")
    
    # Filtros - Guardar preferencias en sesión
    # Si hay parámetros GET, úsalos y guárdalos en la sesión
    if 'estado' in request.GET or 'fecha' in request.GET:
        estado_filtro = request.GET.get('estado', 'todas')
        fecha_filtro = request.GET.get('fecha', 'todas')
        
        # Guardar en sesión
        request.session['entregas_estado_filtro'] = estado_filtro
        request.session['entregas_fecha_filtro'] = fecha_filtro
    else:
        # Recuperar de la sesión o usar valores predeterminados
        estado_filtro = request.session.get('entregas_estado_filtro', 'todas')
        fecha_filtro = request.session.get('entregas_fecha_filtro', 'todas')
    
    # Base queryset
    entregas = EntregaPedido.objects.select_related('pedido', 'empleado_entrega')
    
    # Aplicar filtros de estado
    if estado_filtro != 'todas':
        entregas = entregas.filter(estado_entrega=estado_filtro)
    
    # Obtener las entregas en camino (siempre visibles)
    entregas_en_camino_query = EntregaPedido.objects.filter(estado_entrega='en_camino')
    
    # Aplicar filtros de fecha a las demás entregas
    hoy = timezone.now().date()
    if fecha_filtro == 'hoy':
        entregas_filtradas = entregas.filter(fecha_programada__date=hoy)
        # Unir con entregas en camino
        entregas = entregas_filtradas | entregas_en_camino_query
    elif fecha_filtro == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        entregas_filtradas = entregas.filter(fecha_programada__date__range=[inicio_semana, fin_semana])
        # Unir con entregas en camino
        entregas = entregas_filtradas | entregas_en_camino_query
    elif fecha_filtro == 'mes':
        entregas_filtradas = entregas.filter(fecha_programada__year=hoy.year, fecha_programada__month=hoy.month)
        # Unir con entregas en camino
        entregas = entregas_filtradas | entregas_en_camino_query
    # 'todas' no aplica filtro, se muestran todas las entregas
    
    # Mostrar todas las entregas para empleados de recibos_obra y admin
    # (Ya no filtramos por empleado asignado)
    
    # Estadísticas
    total_entregas = entregas.count()
    entregas_pendientes = entregas.filter(estado_entrega='programada').count()
    entregas_en_camino = entregas.filter(estado_entrega='en_camino').count()
    entregas_completadas = entregas.filter(estado_entrega='entregada').count()
    
    context = {
        'entregas': entregas.order_by('-fecha_programada'),
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro,
        'estadisticas': {
            'total': total_entregas,
            'pendientes': entregas_pendientes,
            'en_camino': entregas_en_camino,
            'completadas': entregas_completadas,
        },
        'estados_choices': EntregaPedido.ESTADO_ENTREGA_CHOICES,
    }
    
    return render(request, 'entregas/panel_entregas.html', context)

@login_required
@user_passes_test(es_empleado_recibos)
def detalle_entrega(request, entrega_id):
    """Detalle de una entrega específica"""
    entrega = get_object_or_404(EntregaPedido, id=entrega_id)
    
    # Verificar permisos - permitir a todos los empleados de recibos_obra ver cualquier entrega
    if request.user.rol != 'recibos_obra' and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para ver esta entrega.')
        return redirect('pedidos:panel_entregas')
    
    context = {
        'entrega': entrega,
        'pedido': entrega.pedido,
        'puede_editar': True,
    }
    
    return render(request, 'entregas/detalle_entrega.html', context)

@login_required
@user_passes_test(es_empleado_recibos)
def iniciar_recorrido(request, entrega_id):
    """Iniciar el recorrido de una entrega"""
    entrega = get_object_or_404(EntregaPedido, id=entrega_id)
    
    # Verificar permisos - permitir a todos los empleados de recibos_obra iniciar cualquier entrega
    if request.user.rol != 'recibos_obra' and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para esta entrega.')
        return redirect('pedidos:panel_entregas')
    
    # Verificar que la entrega esté en estado correcto
    if entrega.estado_entrega != 'programada':
        messages.error(request, f'La entrega debe estar en estado "programada" para iniciar el recorrido. Estado actual: {entrega.get_estado_entrega_display()}')
        return redirect('pedidos:detalle_entrega', entrega_id=entrega.id)
    
    if request.method == 'POST':
        try:
            # Obtener coordenadas GPS si están disponibles
            latitud = request.POST.get('latitud', '0')
            longitud = request.POST.get('longitud', '0')
            
            print(f"DEBUG: Iniciando recorrido para entrega {entrega.id}")
            print(f"DEBUG: Latitud: {latitud}, Longitud: {longitud}")
            print(f"DEBUG: Estado actual: {entrega.estado_entrega}")
            print(f"DEBUG: Usuario: {request.user.username}, Rol: {request.user.rol}")
            print(f"DEBUG: Empleado asignado: {entrega.empleado_entrega.username}")
            
            # Usar coordenadas por defecto si son inválidas o están vacías
            try:
                lat_decimal = Decimal(latitud) if latitud and latitud != 'null' else Decimal('0')
                lon_decimal = Decimal(longitud) if longitud and longitud != 'null' else Decimal('0')
            except:
                print("ERROR: Coordenadas inválidas, usando valores por defecto")
                lat_decimal = Decimal('0')
                lon_decimal = Decimal('0')
            
            # Iniciar recorrido
            entrega.iniciar_recorrido(
                latitud_inicial=lat_decimal,
                longitud_inicial=lon_decimal
            )
            
            messages.success(request, f'Recorrido iniciado correctamente para el pedido {entrega.pedido.id_pedido}')
            return redirect('pedidos:seguimiento_entrega', entrega_id=entrega.id)
            
        except Exception as e:
            import traceback
            print(f"ERROR al iniciar recorrido: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error al iniciar el recorrido: {str(e)}')
            return redirect('pedidos:detalle_entrega', entrega_id=entrega.id)
    
    context = {
        'entrega': entrega,
    }
    
    return render(request, 'entregas/iniciar_recorrido.html', context)

@login_required
@user_passes_test(es_empleado_recibos)
def seguimiento_entrega(request, entrega_id):
    """Página de seguimiento en tiempo real de una entrega"""
    entrega = get_object_or_404(EntregaPedido, id=entrega_id)
    
    # Verificar permisos - permitir a todos los empleados de recibos_obra ver cualquier entrega
    if request.user.rol != 'recibos_obra' and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para ver esta entrega.')
        return redirect('pedidos:panel_entregas')
    
    context = {
        'entrega': entrega,
        'pedido': entrega.pedido,
        'puede_actualizar': True,
    }
    
    return render(request, 'entregas/seguimiento_entrega.html', context)

@login_required
@user_passes_test(es_empleado_recibos)
@csrf_exempt
@require_http_methods(["POST"])
def actualizar_ubicacion(request):
    """API para actualizar la ubicación GPS del vehículo"""
    try:
        data = json.loads(request.body)
        entrega_id = data.get('entrega_id')
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        tiempo_estimado = data.get('tiempo_estimado')
        distancia_restante = data.get('distancia_restante')
        
        entrega = get_object_or_404(EntregaPedido, id=entrega_id)
        
        # Verificar permisos - permitir a todos los empleados de recibos_obra actualizar cualquier entrega
        if request.user.rol not in ['recibos_obra', 'admin']:
            return JsonResponse({'error': 'Sin permisos para actualizar ubicación'}, status=403)
        
        # Actualizar ubicación
        entrega.actualizar_ubicacion(
            latitud=Decimal(str(latitud)),
            longitud=Decimal(str(longitud)),
            tiempo_estimado=datetime.fromisoformat(tiempo_estimado) if tiempo_estimado else None,
            distancia_restante=Decimal(str(distancia_restante)) if distancia_restante else None
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Ubicación actualizada correctamente',
            'ultima_actualizacion': entrega.ultima_actualizacion_gps.isoformat() if entrega.ultima_actualizacion_gps else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@user_passes_test(es_empleado_recibos)
def confirmar_entrega(request, entrega_id):
    """Confirmar la entrega del pedido"""
    entrega = get_object_or_404(EntregaPedido, id=entrega_id)
    
    # Verificar permisos - permitir a todos los empleados de recibos_obra confirmar cualquier entrega
    if request.user.rol != 'recibos_obra' and request.user.rol != 'admin':
        messages.error(request, 'No tienes permisos para esta entrega.')
        return redirect('pedidos:panel_entregas')
    
    if request.method == 'POST':
        # Procesar archivos de confirmación
        if 'firma_recepcion' in request.FILES:
            entrega.firma_recepcion = request.FILES['firma_recepcion']
        if 'foto_entrega' in request.FILES:
            entrega.foto_entrega = request.FILES['foto_entrega']
        
        # Observaciones
        entrega.observaciones = request.POST.get('observaciones', '')
        
        # Confirmar entrega
        entrega.confirmar_entrega()
        
        messages.success(request, f'Entrega confirmada para el pedido {entrega.pedido.id_pedido}. El contador de devolución ha iniciado.')
        return redirect('pedidos:panel_entregas')
    
    context = {
        'entrega': entrega,
    }
    
    return render(request, 'entregas/confirmar_entrega.html', context)

# Vistas para clientes
@login_required
def seguimiento_cliente(request, pedido_id):
    """Seguimiento de entrega para el cliente"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar que el cliente tenga acceso al pedido
    if request.user.rol == 'cliente' and pedido.cliente.usuario != request.user:
        messages.error(request, 'No tienes acceso a este pedido.')
        return redirect('pedidos:mis_pedidos')
    
    try:
        entrega = pedido.entrega
    except EntregaPedido.DoesNotExist:
        messages.info(request, 'Este pedido aún no tiene programada su entrega.')
        return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
    
    context = {
        'pedido': pedido,
        'entrega': entrega,
        'puede_ver_ubicacion': entrega.estado_entrega == 'en_camino',
    }
    
    return render(request, 'entregas/seguimiento_cliente.html', context)

@login_required
@require_http_methods(["GET"])
def api_ubicacion_entrega(request, pedido_id):
    """API para obtener la ubicación actual de una entrega (para cliente)"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar permisos
    if request.user.rol == 'cliente' and pedido.cliente.usuario != request.user:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        entrega = pedido.entrega
        
        if entrega.estado_entrega != 'en_camino':
            return JsonResponse({
                'estado': entrega.estado_entrega,
                'mensaje': f'La entrega está {entrega.get_estado_entrega_display().lower()}'
            })
        
        return JsonResponse({
            'estado': entrega.estado_entrega,
            'latitud': float(entrega.latitud_actual) if entrega.latitud_actual else None,
            'longitud': float(entrega.longitud_actual) if entrega.longitud_actual else None,
            'tiempo_estimado_llegada': entrega.tiempo_estimado_llegada.isoformat() if entrega.tiempo_estimado_llegada else None,
            'distancia_restante_km': float(entrega.distancia_restante_km) if entrega.distancia_restante_km else None,
            'conductor_nombre': entrega.conductor_nombre,
            'conductor_telefono': entrega.conductor_telefono,
            'vehiculo_placa': entrega.vehiculo_placa,
            'ultima_actualizacion': entrega.ultima_actualizacion_gps.isoformat() if entrega.ultima_actualizacion_gps else None
        })
        
    except EntregaPedido.DoesNotExist:
        return JsonResponse({'error': 'Entrega no encontrada'}, status=404)

@login_required
@user_passes_test(lambda u: u.rol in ['admin', 'recibos_obra'])
def programar_entrega(request, pedido_id):
    """Programar una nueva entrega para un pedido"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar que el pedido esté elegible para entrega
    estados_validos = ['pagado', 'en_preparacion', 'listo_entrega']
    if pedido.estado_pedido_general not in estados_validos:
        messages.error(request, f'El pedido debe tener un estado válido para entrega. Estado actual: {pedido.get_estado_pedido_general_display()}')
        return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
    
    # Verificar que no tenga una entrega ya programada
    if hasattr(pedido, 'entrega'):
        messages.info(request, 'Este pedido ya tiene una entrega programada.')
        return redirect('pedidos:detalle_entrega', entrega_id=pedido.entrega.id)
    
    if request.method == 'POST':
        # Crear nueva entrega
        entrega = EntregaPedido.objects.create(
            pedido=pedido,
            empleado_entrega_id=request.POST.get('empleado_entrega'),
            fecha_programada=request.POST.get('fecha_programada'),
            direccion_salida=request.POST.get('direccion_salida'),
            direccion_destino=pedido.direccion_entrega,
            vehiculo_placa=request.POST.get('vehiculo_placa'),
            conductor_nombre=request.POST.get('conductor_nombre'),
            conductor_telefono=request.POST.get('conductor_telefono'),
            observaciones=request.POST.get('observaciones', '')
        )
        
        messages.success(request, f'Entrega programada correctamente para el pedido {pedido.id_pedido}')
        return redirect('pedidos:detalle_entrega', entrega_id=entrega.id)
    
    # Obtener empleados de recibos de obra
    empleados_recibos = Usuario.objects.filter(rol='recibos_obra', activo=True)
    
    context = {
        'pedido': pedido,
        'empleados_recibos': empleados_recibos,
    }
    
    return render(request, 'entregas/programar_entrega.html', context)

@login_required
@user_passes_test(es_empleado_recibos)
def pedidos_listos_entrega(request):
    """Lista de pedidos pagados listos para programar entrega"""
    
    # Filtros
    cliente_filtro = request.GET.get('cliente', '')
    fecha_filtro = request.GET.get('fecha', 'todas')
    
    # Obtener pedidos con pago aceptado que no tienen entrega programada
    pedidos = Pedido.objects.filter(
        estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega']
    ).exclude(
        entrega__isnull=False  # Excluir pedidos que ya tienen entrega programada
    ).select_related('cliente')
    
    # Aplicar filtros
    if cliente_filtro:
        pedidos = pedidos.filter(
            Q(cliente__usuario__first_name__icontains=cliente_filtro) |
            Q(cliente__usuario__last_name__icontains=cliente_filtro) |
            Q(cliente__usuario__username__icontains=cliente_filtro)
        )
    
    # Filtro por fecha
    hoy = timezone.now().date()
    if fecha_filtro == 'hoy':
        pedidos = pedidos.filter(fecha_pago__date=hoy)
    elif fecha_filtro == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        pedidos = pedidos.filter(fecha_pago__date__range=[inicio_semana, fin_semana])
    elif fecha_filtro == 'mes':
        pedidos = pedidos.filter(fecha_pago__year=hoy.year, fecha_pago__month=hoy.month)
    
    # Estadísticas
    total_pedidos = pedidos.count()
    pedidos_pagados = pedidos.filter(estado_pedido_general='pagado').count()
    pedidos_preparacion = pedidos.filter(estado_pedido_general='en_preparacion').count()
    pedidos_listos = pedidos.filter(estado_pedido_general='listo_entrega').count()
    
    context = {
        'pedidos': pedidos.order_by('-fecha_pago'),
        'cliente_filtro': cliente_filtro,
        'fecha_filtro': fecha_filtro,
        'estadisticas': {
            'total': total_pedidos,
            'pagados': pedidos_pagados,
            'en_preparacion': pedidos_preparacion,
            'listos': pedidos_listos,
        },
    }
    
    return render(request, 'entregas/pedidos_listos_entrega.html', context)

@login_required
@user_passes_test(es_admin)
def seguimientos_admin(request):
    """Vista para que el admin vea todos los seguimientos de envío"""
    # Obtener todas las entregas con seguimiento activo
    entregas_activas = EntregaPedido.objects.select_related(
        'pedido', 'pedido__cliente', 'pedido__cliente__usuario'
    ).filter(
        estado_entrega__in=['programada', 'en_camino', 'entregada']
    ).order_by('-fecha_programada')
    
    # Filtros opcionales
    estado_filtro = request.GET.get('estado', 'todas')
    if estado_filtro != 'todas':
        entregas_activas = entregas_activas.filter(estado_entrega=estado_filtro)
    
    # Filtro por fecha
    fecha_filtro = request.GET.get('fecha', 'todas')
    if fecha_filtro == 'hoy':
        hoy = timezone.now().date()
        entregas_activas = entregas_activas.filter(fecha_programada=hoy)
    elif fecha_filtro == 'semana':
        desde = timezone.now().date()
        hasta = desde + timedelta(days=7)
        entregas_activas = entregas_activas.filter(fecha_programada__range=[desde, hasta])
    
    # Estadísticas rápidas
    stats = {
        'total': entregas_activas.count(),
        'programadas': entregas_activas.filter(estado_entrega='programada').count(),
        'en_camino': entregas_activas.filter(estado_entrega='en_camino').count(),
        'entregadas': entregas_activas.filter(estado_entrega='entregada').count(),
    }
    
    context = {
        'entregas': entregas_activas,
        'stats': stats,
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro,
    }
    
    return render(request, 'entregas/seguimientos_admin.html', context)
