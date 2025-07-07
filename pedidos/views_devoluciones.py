from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction, models
from django.urls import reverse

from .models import Pedido, DetallePedido, DevolucionParcial, ExtensionRenta
from productos.models import Producto
from recibos.models import ReciboObra, DetalleReciboObra
from usuarios.decorators import requiere_permiso, verificar_permisos_modulo

def puede_ver_pedidos(user):
    return verificar_permisos_modulo(user, 'pedidos')

import logging
logger = logging.getLogger(__name__)

@login_required
@user_passes_test(puede_ver_pedidos)
def registrar_devolucion_parcial(request, pedido_id):
    """
    Vista para registrar la devolución parcial de productos de un pedido
    """
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Obtener solo los detalles que están en estado 'entregado' o 'devuelto_parcial'
    detalles_disponibles = pedido.detalles.filter(
        estado__in=['entregado', 'devuelto_parcial'],
        cantidad_devuelta__lt=models.F('cantidad')
    )
    
    if not detalles_disponibles.exists():
        messages.warning(request, "No hay productos disponibles para devolución parcial en este pedido.")
        return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
    
    if request.method == 'POST':
        errores = []
        productos_procesados = []
        
        try:
            with transaction.atomic():
                # Procesar cada detalle
                for detalle in detalles_disponibles:
                    cantidad_key = f'cantidad_{detalle.id}'
                    estado_key = f'estado_{detalle.id}'
                    notas_key = f'notas_{detalle.id}'
                    
                    if cantidad_key in request.POST and request.POST.get(cantidad_key):
                        cantidad = int(request.POST.get(cantidad_key))
                        estado = request.POST.get(estado_key, 'buen_estado')
                        notas = request.POST.get(notas_key, '')
                        
                        # Validar la cantidad
                        if cantidad <= 0:
                            continue  # Ignorar cantidades 0 o negativas
                            
                        cantidad_pendiente = detalle.cantidad - detalle.cantidad_devuelta
                        if cantidad > cantidad_pendiente:
                            errores.append(f"La cantidad para {detalle.producto.nombre} excede la pendiente ({cantidad_pendiente}).")
                            continue
                        
                        # Crear registro de devolución parcial
                        DevolucionParcial.objects.create(
                            detalle_pedido=detalle,
                            cantidad=cantidad,
                            estado=estado,
                            notas=notas,
                            procesado_por=request.user
                        )
                        
                        # Actualizar el DetallePedido
                        detalle.cantidad_devuelta += cantidad
                        
                        # Verificar si se han devuelto todos los productos o solo algunos
                        if detalle.cantidad_devuelta >= detalle.cantidad:
                            detalle.estado = 'devuelto'
                        else:
                            detalle.estado = 'devuelto_parcial'
                        
                        detalle.save()
                
                        # Registrar producto procesado
                        productos_procesados.append(f"{cantidad} de {detalle.producto.nombre}")
                # Si no se procesó ningún producto, lanzar error
                if not productos_procesados:
                    raise ValueError("No se ha registrado ninguna devolución. Verifica los datos ingresados.")
                
                # Si hay productos para extender renta, redirigir a esa vista
                if 'extender_renta' in request.POST and request.POST.get('extender_renta') == 'si':
                    # Redireccionar a la vista de extensión de renta
                    messages.success(request, f"Devolución parcial registrada: {', '.join(productos_procesados)}.")
                    return redirect('pedidos:extender_renta', pedido_id=pedido_id)
                
                messages.success(request, f"Devolución parcial registrada: {', '.join(productos_procesados)}.")
                return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error al registrar devolución parcial: {str(e)}")
            messages.error(request, f"Error al registrar la devolución parcial: {str(e)}")
    
    return render(request, 'pedidos/registrar_devolucion_parcial.html', {
        'pedido': pedido,
        'detalles': detalles_disponibles,
    })

@login_required
@user_passes_test(puede_ver_pedidos)
def extender_renta(request, pedido_id):
    """
    Vista para extender la renta de productos que han sido devueltos parcialmente
    """
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Obtener detalles con devoluciones parciales
    detalles_parciales = pedido.detalles.filter(
        estado='devuelto_parcial',
        renta_extendida=False  # Solo mostrar los que no han sido extendidos
    )
    
    if not detalles_parciales.exists():
        messages.warning(request, "No hay productos con devolución parcial para extender renta.")
        return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
    
    if request.method == 'POST':
        errores = []
        extensiones_registradas = []
        
        try:
            with transaction.atomic():
                # Procesar cada detalle
                for detalle in detalles_parciales:
                    extender_key = f'extender_{detalle.id}'
                    dias_key = f'dias_{detalle.id}'
                    notas_key = f'notas_{detalle.id}'
                    
                    if extender_key in request.POST and request.POST.get(extender_key) == 'si':
                        try:
                            dias = int(request.POST.get(dias_key, 0))
                            notas = request.POST.get(notas_key, '')
                            
                            # Validar días
                            if dias <= 0:
                                errores.append(f"Los días adicionales para {detalle.producto.nombre} deben ser mayores a 0.")
                                continue
                                
                            # Calcular cantidad restante
                            cantidad_restante = detalle.cantidad - detalle.cantidad_devuelta
                            
                            # Crear extensión de renta
                            ExtensionRenta.objects.create(
                                detalle_pedido=detalle,
                                dias_adicionales=dias,
                                cantidad=cantidad_restante,
                                precio_diario=detalle.precio_diario,
                                notas=notas,
                                procesado_por=request.user
                            )
                            
                            # Actualizar el DetallePedido para indicar que la renta fue extendida
                            detalle.renta_extendida = True
                            detalle.save()
                            
                            # Registrar extensión
                            extensiones_registradas.append(f"{cantidad_restante} de {detalle.producto.nombre} por {dias} días")
                            
                        except ValueError:
                            errores.append(f"Valor inválido para los días adicionales de {detalle.producto.nombre}.")
                
                # Si no se procesó ninguna extensión, lanzar error
                if not extensiones_registradas:
                    raise ValueError("No se ha registrado ninguna extensión de renta. Verifica los datos ingresados.")
                
                messages.success(request, f"Extensión de renta registrada: {', '.join(extensiones_registradas)}.")
                return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error al registrar extensión de renta: {str(e)}")
            messages.error(request, f"Error al registrar la extensión de renta: {str(e)}")
    
    return render(request, 'pedidos/extender_renta.html', {
        'pedido': pedido,
        'detalles': detalles_parciales,
    })

@login_required
def seleccion_devolucion_parcial(request, pedido_id):
    """
    Vista para que el cliente seleccione qué productos devolver y cuáles extender
    al final del período de renta
    """
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar que el usuario tenga permiso para ver este pedido
    # Los clientes solo pueden ver sus propios pedidos
    if not request.user.is_staff and pedido.cliente.usuario != request.user:
        messages.error(request, "No tienes permiso para acceder a este pedido.")
        return redirect('usuarios:inicio')
    
    # Verificar que el pedido está en estado correcto
    estados_validos = ['recibido', 'programado_devolucion', 'entregado']
    if pedido.estado_pedido_general not in estados_validos:
        messages.warning(request, f"Este pedido no está listo para devolución parcial. Estado actual: {pedido.get_estado_pedido_general_display()}")
        # Redirigir según el tipo de usuario
        if request.user.is_staff:
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
        else:
            return redirect('pedidos:detalle_mi_pedido', pedido_id=pedido_id)
    
    # Obtener detalles del pedido que pueden ser devueltos o extendidos
    # Incluir productos en estado 'entregado' o 'devuelto_parcial' (que aún tienen productos pendientes)
    detalles_disponibles = pedido.detalles.filter(
        estado__in=['entregado', 'devuelto_parcial']
    ).exclude(
        # Excluir productos que ya han sido completamente devueltos
        cantidad_devuelta__gte=models.F('cantidad')
    )
    
    # Log de diagnóstico
    logger.info(f"=== DIAGNÓSTICO DEVOLUCIÓN PARCIAL ===")
    logger.info(f"Pedido ID: {pedido_id}")
    logger.info(f"Estado del pedido: {pedido.estado_pedido_general}")
    logger.info(f"Total detalles en el pedido: {pedido.detalles.count()}")
    
    # Mostrar información de todos los detalles para diagnóstico
    for detalle in pedido.detalles.all():
        logger.info(f"Detalle ID {detalle.id}: {detalle.producto.nombre} - Estado: {detalle.estado} - Cantidad: {detalle.cantidad} - Devuelta: {detalle.cantidad_devuelta}")
    
    logger.info(f"Detalles disponibles para devolución: {detalles_disponibles.count()}")
    
    if not detalles_disponibles.exists():
        # Mensaje más específico para el usuario
        total_detalles = pedido.detalles.count()
        detalles_entregados = pedido.detalles.filter(estado__in=['entregado', 'devuelto_parcial']).count()
        
        mensaje_debug = f"No hay productos disponibles para devolver o extender en este pedido. "
        mensaje_debug += f"Total productos: {total_detalles}, "
        mensaje_debug += f"Productos entregados/parcialmente devueltos: {detalles_entregados}. "
        mensaje_debug += f"Estados encontrados: {list(pedido.detalles.values_list('estado', flat=True))}"
        
        messages.warning(request, mensaje_debug)
        
        # Redirigir según el tipo de usuario
        if request.user.is_staff:
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
        else:
            return redirect('pedidos:detalle_mi_pedido', pedido_id=pedido_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Variables para llevar el conteo
                productos_devueltos = []
                productos_extendidos = []
                
                # Estado de devolución general
                estado_devolucion = request.POST.get('estado_devolucion', 'buen_estado')
                notas_devolucion = request.POST.get('notas_devolucion', '')
                
                # Variables para el recibo de devolución
                crear_recibo_devolucion = False
                detalles_recibo_devolucion = []
                
                # Variables para extensiones de renta
                crear_extensiones = False
                extensiones_a_crear = []
                
                # Procesar cada detalle del pedido
                for detalle in detalles_disponibles:
                    # Obtener datos del formulario
                    accion = request.POST.get(f'accion_{detalle.id}', '')
                    cantidad_devolver = int(request.POST.get(f'devolver_{detalle.id}', 0) or 0)
                    cantidad_extender = int(request.POST.get(f'extender_{detalle.id}', 0) or 0)
                    dias_adicionales = int(request.POST.get(f'dias_{detalle.id}', 7) or 7)
                    
                    # Validar que la suma de cantidades sea correcta
                    if cantidad_devolver + cantidad_extender != detalle.cantidad:
                        raise ValueError(f"La suma de cantidades a devolver y extender para {detalle.producto.nombre} no coincide con la cantidad total.")
                    
                    # Procesar devolución si aplica
                    if cantidad_devolver > 0:
                        crear_recibo_devolucion = True
                        # Crear registro para el recibo de devolución
                        detalles_recibo_devolucion.append({
                            'detalle_pedido': detalle,
                            'producto': detalle.producto,
                            'cantidad': cantidad_devolver,
                            'estado': estado_devolucion
                        })
                        
                        # Registrar devolución parcial en el modelo
                        DevolucionParcial.objects.create(
                            detalle_pedido=detalle,
                            cantidad=cantidad_devolver,
                            estado=estado_devolucion,
                            notas=notas_devolucion,
                            procesado_por=request.user
                        )
                        
                        # Actualizar el DetallePedido
                        detalle.cantidad_devuelta += cantidad_devolver
                        
                        # Verificar si se han devuelto todos los productos o solo algunos
                        if cantidad_extender == 0:
                            detalle.estado = 'devuelto'
                        else:
                            detalle.estado = 'devuelto_parcial'
                        
                        detalle.save()
                        productos_devueltos.append(f"{cantidad_devolver} de {detalle.producto.nombre}")
                    
                    # Procesar extensión si aplica
                    if cantidad_extender > 0:
                        crear_extensiones = True
                        precio_diario = detalle.precio_diario
                        subtotal = precio_diario * cantidad_extender * dias_adicionales
                        
                        # Crear extensión de renta
                        extensiones_a_crear.append({
                            'detalle_pedido': detalle,
                            'dias_adicionales': dias_adicionales,
                            'cantidad': cantidad_extender,
                            'precio_diario': precio_diario,
                            'subtotal': subtotal,
                            'notas': f"Extensión por devolución parcial al final del período de renta",
                            'procesado_por': request.user
                        })
                        
                        productos_extendidos.append(f"{cantidad_extender} de {detalle.producto.nombre} por {dias_adicionales} días")
                
                # Crear recibo de devolución si es necesario
                if crear_recibo_devolucion:
                    # Crear el recibo principal
                    recibo = ReciboObra.objects.create(
                        pedido=pedido,
                        cliente=pedido.cliente,
                        notas_entrega=notas_devolucion,
                        condicion_entrega=f"Devolución parcial al final del período de renta - {dict(DevolucionParcial.ESTADO_CHOICES)[estado_devolucion]}",
                        empleado=request.user,
                        es_recibo_devolucion=True
                    )
                    
                    # Crear los detalles del recibo
                    for detalle_info in detalles_recibo_devolucion:
                        DetalleReciboObra.objects.create(
                            recibo=recibo,
                            producto=detalle_info['producto'],
                            detalle_pedido=detalle_info['detalle_pedido'],
                            cantidad_solicitada=detalle_info['cantidad'],
                            cantidad_vuelta=detalle_info['cantidad'],  # Ya está devuelto
                            estado='DEVUELTO'
                        )
                
                # Crear extensiones de renta si es necesario
                if crear_extensiones:
                    for extension_info in extensiones_a_crear:
                        ExtensionRenta.objects.create(
                            detalle_pedido=extension_info['detalle_pedido'],
                            dias_adicionales=extension_info['dias_adicionales'],
                            cantidad=extension_info['cantidad'],
                            precio_diario=extension_info['precio_diario'],
                            subtotal=extension_info['subtotal'],
                            notas=extension_info['notas'],
                            procesado_por=extension_info['procesado_por']
                        )
                        
                        # Marcar el detalle como extendido
                        detalle_pedido = extension_info['detalle_pedido']
                        detalle_pedido.renta_extendida = True
                        detalle_pedido.save()
                
                # Mostrar mensaje de éxito
                mensajes = []
                if productos_devueltos:
                    mensajes.append(f"Productos devueltos: {', '.join(productos_devueltos)}")
                if productos_extendidos:
                    mensajes.append(f"Productos con renta extendida: {', '.join(productos_extendidos)}")
                
                messages.success(request, " | ".join(mensajes))
                
                # Si no queda nada por devolver, cerrar el pedido
                if not pedido.detalles.filter(estado__in=['entregado', 'devuelto_parcial']).exclude(renta_extendida=True).exists():
                    pedido.estado_pedido_general = 'cerrado'
                    pedido.save()
                    messages.info(request, "Todas las operaciones han sido completadas. El pedido ha sido cerrado.")
                
                return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error al procesar selección de devolución parcial: {str(e)}")
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")
    
    return render(request, 'pedidos/seleccion_devolucion_parcial.html', {
        'pedido': pedido,
        'detalles': detalles_disponibles,
    })

@login_required
def cambiar_estado_productos_pedido(request, pedido_id):
    """
    Vista temporal para cambiar el estado de productos de un pedido
    para permitir devoluciones parciales
    """
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('usuarios:inicio')
    
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado', 'entregado')
        cantidad_productos_actualizados = 0
        
        for detalle in pedido.detalles.all():
            detalle.estado = nuevo_estado
            detalle.save()
            cantidad_productos_actualizados += 1
        
        messages.success(request, f"Se han actualizado {cantidad_productos_actualizados} productos al estado '{nuevo_estado}'.")
        return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
    
    return render(request, 'pedidos/cambiar_estado_productos.html', {
        'pedido': pedido,
        'estados': DetallePedido.ESTADO_CHOICES,
    })
