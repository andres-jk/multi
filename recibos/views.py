from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Q, Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
from .models import ReciboObra, DetalleReciboObra
from pedidos.models import Pedido, DetallePedido
from usuarios.models import Cliente
from productos.models import Producto

def es_staff(user):
    return user.is_staff or user.rol in ['admin', 'empleado']

def puede_ver_recibos(user):
    """Verifica si un usuario puede acceder a la sección de recibos de obra"""
    return user.is_staff or user.rol in ['admin', 'recibos_obra']

@login_required
@user_passes_test(puede_ver_recibos)
def lista_recibos(request):
    """Vista para listar todos los recibos de obra con funcionalidad de búsqueda"""
    recibos = ReciboObra.objects.all()
    
    # Búsqueda por pedido, cliente o producto
    search_query = request.GET.get('search', '')
    if search_query:
        try:
            # Intentar buscar por ID de pedido si es un número
            pedido_id = int(search_query)
            pedidos_match = recibos.filter(pedido__id_pedido=pedido_id)
            if pedidos_match.exists():
                recibos = pedidos_match
            else:
                # Buscar en cliente o producto
                from django.db.models import Q
                recibos = recibos.filter(
                    Q(cliente__usuario__first_name__icontains=search_query) |
                    Q(cliente__usuario__last_name__icontains=search_query) |
                    Q(producto__nombre__icontains=search_query)
                )
        except ValueError:
            # Si no es un número, buscar por nombre de cliente o producto
            from django.db.models import Q
            recibos = recibos.filter(
                Q(cliente__usuario__first_name__icontains=search_query) |
                Q(cliente__usuario__last_name__icontains=search_query) |
                Q(producto__nombre__icontains=search_query)
            )
    
    recibos = recibos.order_by('-fecha_entrega')
    
    return render(request, 'recibos/lista_recibos.html', {
        'recibos': recibos, 
        'solo_recibos': request.user.rol == 'recibos_obra',
        'search_query': search_query
    })

@login_required
@user_passes_test(puede_ver_recibos)
def crear_recibo(request, pedido_id):
    """Vista para crear un nuevo recibo de obra"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('producto')
            cantidad = int(request.POST.get('cantidad'))
            notas = request.POST.get('notas', '')
            condicion = request.POST.get('condicion', '')
            
            # Validar que el producto pertenezca al pedido
            detalle = pedido.detalles.filter(producto_id=producto_id).first()
            if not detalle:
                messages.error(request, "El producto seleccionado no pertenece a este pedido.")
                return redirect('recibos:crear_recibo', pedido_id=pedido_id)
              # Verificar que hay suficiente cantidad en renta
            producto = get_object_or_404(Producto, id_producto=producto_id)
            
            if cantidad > 0:
                # Para recibos nuevos, asumimos que los productos están "en renta"
                # Si no hay suficiente en renta, los movemos desde disponible (corrección de inconsistencia)
                if producto.cantidad_en_renta < cantidad:
                    faltante = cantidad - producto.cantidad_en_renta
                    if producto.cantidad_disponible >= faltante:
                        # Movemos productos disponibles a en renta
                        producto.cantidad_disponible -= faltante
                        producto.cantidad_en_renta += faltante
                        producto.save()
                        print(f"Corregido: movidos {faltante} productos de disponible a en renta")
                        messages.info(request, f"Se han movido {faltante} unidades de disponible a en renta para corregir inconsistencia")
                    else:
                        messages.error(request, f"No hay suficientes productos disponibles o en renta para crear el recibo: {cantidad} solicitados, {producto.cantidad_en_renta} en renta, {producto.cantidad_disponible} disponibles")
                        return redirect('recibos:crear_recibo', pedido_id=pedido_id)
            
            # Crear el recibo
            recibo = ReciboObra.objects.create(
                pedido=pedido,
                cliente=pedido.cliente,
                producto_id=producto_id,
                cantidad_solicitada=cantidad,
                notas_entrega=notas,
                condicion_entrega=condicion,
                empleado=request.user
            )
            
            messages.success(request, f"Recibo de obra #{recibo.id} creado exitosamente.")
            return redirect('recibos:generar_pdf', recibo_id=recibo.id)
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error al crear el recibo: {str(e)}")
    
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all(),
    }
    return render(request, 'recibos/crear_recibo.html', context)

@login_required
@user_passes_test(puede_ver_recibos)
def registrar_devolucion(request, recibo_id):
    """Vista para registrar la devolución de equipos"""
    recibo = get_object_or_404(ReciboObra, id=recibo_id)
    
    if request.method == 'POST':
        try:
            cantidad_buen_estado = int(request.POST.get('cantidad_buen_estado', 0))
            cantidad_danados = int(request.POST.get('cantidad_danados', 0))
            cantidad_inservibles = int(request.POST.get('cantidad_inservibles', 0))
            estado = request.POST.get('estado')
            notas = request.POST.get('notas', '')
            condicion = request.POST.get('condicion', '')
            
            # Validar cantidades negativas
            if cantidad_buen_estado < 0 or cantidad_danados < 0 or cantidad_inservibles < 0:
                raise ValueError("Las cantidades no pueden ser negativas.")
                
            # Calcular la cantidad total devuelta
            cantidad_total = cantidad_buen_estado + cantidad_danados + cantidad_inservibles
            
            # Validar que se esté devolviendo al menos 1 producto
            if cantidad_total == 0:
                raise ValueError("Debes registrar la devolución de al menos un producto.")
                
            # Validar que la cantidad no exceda la pendiente
            cantidad_pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
            if cantidad_total > cantidad_pendiente:
                raise ValueError(f"La cantidad total devuelta ({cantidad_total}) no puede ser mayor a la cantidad pendiente ({cantidad_pendiente}).")
              # Actualizar el recibo
            recibo.cantidad_buen_estado += cantidad_buen_estado
            recibo.cantidad_danados += cantidad_danados
            recibo.cantidad_inservibles += cantidad_inservibles
            recibo.cantidad_vuelta += cantidad_total
            recibo.estado = estado
            recibo.notas_devolucion = notas
            recibo.condicion_devolucion = condicion
            recibo.fecha_devolucion = timezone.now()
            recibo.save()
              # Devolver al inventario los productos en buen estado
            if cantidad_buen_estado > 0 and recibo.producto:
                try:
                    # Obtener el producto correctamente
                    producto_id = recibo.producto.id_producto
                    
                    # Asegurarse de obtener una instancia fresca del producto para evitar problemas de caché
                    producto_actualizado = Producto.objects.get(id_producto=producto_id)
                    
                    # Debug información antes de devolver
                    previous_disponible = producto_actualizado.cantidad_disponible
                    previous_en_renta = producto_actualizado.cantidad_en_renta
                    previous_reservada = producto_actualizado.cantidad_reservada
                    
                    # Imprimir valores para depuración detallada
                    print(f"=== DEVOLUCIÓN DE PRODUCTOS ===")
                    print(f"Producto ID: {producto_id}")
                    print(f"Producto Nombre: {producto_actualizado.nombre}")
                    print(f"Cantidad total del producto: {producto_actualizado.cantidad_total()}")
                    print(f"Cantidad en renta antes: {previous_en_renta}")
                    print(f"Cantidad disponible antes: {previous_disponible}")
                    print(f"Cantidad reservada antes: {previous_reservada}")
                    print(f"Cantidad a devolver: {cantidad_buen_estado}")
                      # Verificar que haya suficiente cantidad en renta
                    if cantidad_buen_estado <= producto_actualizado.cantidad_en_renta:
                        # Flujo normal - tenemos suficientes en renta
                        producto_actualizado.cantidad_en_renta -= cantidad_buen_estado
                        producto_actualizado.cantidad_disponible += cantidad_buen_estado
                        producto_actualizado.save()
                        
                        # Verificar que se haya guardado correctamente
                        producto_verificado = Producto.objects.get(id_producto=producto_id)
                        
                        print(f"Devolución exitosa - Producto {producto_id}")
                        print(f"Cantidad en renta después: {producto_verificado.cantidad_en_renta}")
                        print(f"Cantidad disponible después: {producto_verificado.cantidad_disponible}")
                        print(f"=== FIN DEVOLUCIÓN ===")
                        
                        messages.success(request,
                            f"Se han devuelto {cantidad_buen_estado} unidades en buen estado al inventario. "
                            f"Disponibles antes: {previous_disponible}, después: {producto_verificado.cantidad_disponible}. "
                            f"En renta antes: {previous_en_renta}, después: {producto_verificado.cantidad_en_renta}.")
                    else:
                        # Corregimos inconsistencia: los productos deberían estar en renta pero no lo están
                        # Asumimos que están disponibles (fueron devueltos de otra manera)
                        if producto_actualizado.cantidad_disponible >= cantidad_buen_estado:
                            # No es necesario mover inventario, solo registramos la devolución
                            print(f"NOTA: Los productos ya están disponibles, solo registramos la devolución en el recibo")
                            messages.info(request,
                                f"Los productos ya estaban disponibles en el inventario. Solo se ha registrado la devolución.")
                        else:
                            print(f"ERROR: La cantidad a devolver ({cantidad_buen_estado}) excede tanto la cantidad en renta ({producto_actualizado.cantidad_en_renta}) como la disponible ({producto_actualizado.cantidad_disponible})")
                            print(f"=== FIN DEVOLUCIÓN CON ERROR ===")
                            
                            messages.warning(request, 
                                f"No se pudieron devolver los productos al inventario. La cantidad a devolver ({cantidad_buen_estado}) "
                                f"no está disponible en ningún estado del inventario.")
                except Exception as e:
                    print(f"ERROR en devolución: {str(e)}")
                    messages.error(request, f"Error al procesar la devolución: {str(e)}")
            
            # Marcar el pedido como completado si todos los productos han sido devueltos
            if recibo.cantidad_vuelta >= recibo.cantidad_solicitada:
                recibo.pedido.estado_pedido_general = 'CERRADO'
                recibo.pedido.save()
                messages.info(request, "El pedido ha sido marcado como CERRADO.")
            
            messages.success(request, "Devolución registrada exitosamente.")
            return redirect('recibos:lista_recibos')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error al registrar la devolución: {str(e)}")
    
    # Calculamos el valor máximo para las devoluciones
    cantidad_pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
    
    return render(request, 'recibos/registrar_devolucion.html', {
        'recibo': recibo,
        'cantidad_pendiente': cantidad_pendiente
    })

@login_required
def generar_pdf(request, recibo_id):
    """Vista para generar el PDF del recibo de obra"""
    recibo = get_object_or_404(ReciboObra, id=recibo_id)
    
    # Verificar permisos
    if not request.user.is_staff and recibo.cliente.usuario != request.user:
        messages.error(request, "No tienes permiso para ver este recibo.")
        return redirect('inicio')
    
    # Crear el PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Encabezado
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, f"RECIBO DE OBRA #{recibo.id}")
    
    # Información del cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 100, "INFORMACIÓN DEL CLIENTE")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 120, f"Cliente: {recibo.cliente.usuario.get_full_name()}")
    p.drawString(50, height - 140, f"Identificación: {recibo.cliente.usuario.numero_identidad}")
    p.drawString(50, height - 160, f"Teléfono: {recibo.cliente.telefono}")  # Cambiado de usuario.telefono a cliente.telefono
    
    # Información del equipo
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 200, "INFORMACIÓN DEL EQUIPO")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 220, f"Producto: {recibo.producto.nombre}")
    p.drawString(50, height - 240, f"Cantidad: {recibo.cantidad_solicitada}")
    p.drawString(50, height - 260, f"Fecha de entrega: {recibo.fecha_entrega.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(50, height - 280, f"Estado de entrega: {recibo.condicion_entrega}")
    
    if recibo.fecha_devolucion:
        p.drawString(50, height - 300, f"Fecha de devolución: {recibo.fecha_devolucion.strftime('%d/%m/%Y %H:%M')}")
        p.drawString(50, height - 320, f"Estado de devolución: {recibo.condicion_devolucion or 'No especificado'}")
        p.drawString(50, height - 340, f"Cantidad devuelta: {recibo.cantidad_vuelta}")
    
    # Firmas
    p.setFont("Helvetica", 10)
    p.line(50, 100, 250, 100)  # Línea para firma del cliente
    p.drawString(120, 85, "Firma del Cliente")
    
    p.line(300, 100, 500, 100)  # Línea para firma del empleado
    p.drawString(370, 85, "Firma del Empleado")
    
    # Finalizar PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    
    # Retornar el PDF
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_obra_{recibo.id}.pdf"'
    
    return response

@login_required
@user_passes_test(es_staff)
def resumen_sistema(request):
    """Vista de resumen del sistema para administradores"""
    # Estadísticas de productos
    productos = Producto.objects.all()
    productos_count = productos.count()
    productos_disponibles = productos.aggregate(Sum('cantidad_disponible'))['cantidad_disponible__sum'] or 0
    productos_reservados = productos.aggregate(Sum('cantidad_reservada'))['cantidad_reservada__sum'] or 0
    productos_en_renta = productos.aggregate(Sum('cantidad_en_renta'))['cantidad_en_renta__sum'] or 0
    
    # Estadísticas de pedidos
    pedidos = Pedido.objects.all()
    pedidos_count = pedidos.count()
    pedidos_pendientes = pedidos.filter(estado_pedido_general='PENDIENTE').count()
    pedidos_en_proceso = pedidos.filter(estado_pedido_general='EN_PROCESO').count()
    pedidos_completados = pedidos.filter(estado_pedido_general='CERRADO').count()
    
    # Estadísticas de recibos
    recibos = ReciboObra.objects.all()
    recibos_count = recibos.count()
    recibos_pendientes = recibos.filter(estado='PENDIENTE').count()
    recibos_en_uso = recibos.filter(estado='EN_USO').count()
    recibos_devueltos = recibos.filter(estado='DEVUELTO').count()
    
    # Actividades recientes (simuladas por ahora)
    actividades = [
        {
            'fecha': timezone.now() - timezone.timedelta(hours=2),
            'descripcion': 'Nuevo pedido #12345 creado',
            'usuario': 'Pedro Rodríguez'
        },
        {
            'fecha': timezone.now() - timezone.timedelta(hours=5),
            'descripcion': 'Devolución registrada para recibo #78',
            'usuario': 'María González'
        },
        {
            'fecha': timezone.now() - timezone.timedelta(days=1),
            'descripcion': 'Producto actualizado: Andamio tubular',
            'usuario': 'Juan Pérez'
        }
    ]
    
    return render(request, 'recibos/resumen.html', {
        'productos_count': productos_count,
        'productos_disponibles': productos_disponibles,
        'productos_reservados': productos_reservados,
        'productos_en_renta': productos_en_renta,
        'pedidos_count': pedidos_count,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_en_proceso': pedidos_en_proceso,
        'pedidos_completados': pedidos_completados,
        'recibos_count': recibos_count,
        'recibos_pendientes': recibos_pendientes,
        'recibos_en_uso': recibos_en_uso,
        'recibos_devueltos': recibos_devueltos,
        'actividades': actividades
    })

@login_required
@user_passes_test(puede_ver_recibos)
def registrar_devolucion_multiple(request, pedido_id):
    """Vista para registrar la devolución de múltiples productos de un pedido en una sola operación"""
    print(f"Accediendo a la vista de devolución múltiple para el pedido {pedido_id}")
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
      # Obtener todos los recibos con devoluciones pendientes para este pedido
    from django.db.models import F
    recibos_pendientes = ReciboObra.objects.filter(
        pedido=pedido, 
        cantidad_vuelta__lt=F('cantidad_solicitada')
    )
    
    # Calculamos la cantidad pendiente para cada recibo
    for recibo in recibos_pendientes:
        recibo.cantidad_pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
    
    if request.method == 'POST':
        try:
            # Inicializar contadores para el informe final
            total_buen_estado = 0
            total_danados = 0
            total_inservibles = 0
            recibos_actualizados = 0
            
            # Para cada recibo pendiente, procesar la devolución
            for recibo in recibos_pendientes:
                # Obtener las cantidades desde el formulario
                cantidad_buen_estado = int(request.POST.get(f'buen_estado_{recibo.id}', 0) or 0)
                cantidad_danados = int(request.POST.get(f'danados_{recibo.id}', 0) or 0)
                cantidad_inservibles = int(request.POST.get(f'inservibles_{recibo.id}', 0) or 0)
                
                # Calcular la cantidad total devuelta para este recibo
                cantidad_total_recibo = cantidad_buen_estado + cantidad_danados + cantidad_inservibles
                
                # Si no hay devoluciones para este recibo, continuamos con el siguiente
                if cantidad_total_recibo == 0:
                    continue
                
                # Validar que no exceda la cantidad pendiente
                cantidad_pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
                
                if cantidad_total_recibo > cantidad_pendiente:
                    raise ValueError(f"La cantidad total devuelta para el producto '{recibo.producto.nombre}' ({cantidad_total_recibo}) excede la cantidad pendiente ({cantidad_pendiente}).")
                
                # Actualizar el recibo
                recibo.cantidad_buen_estado += cantidad_buen_estado
                recibo.cantidad_danados += cantidad_danados
                recibo.cantidad_inservibles += cantidad_inservibles
                recibo.cantidad_vuelta += cantidad_total_recibo
                
                # Actualizar el estado del recibo si se devuelve todo
                estado = request.POST.get('estado_general', 'PENDIENTE')
                if recibo.cantidad_vuelta >= recibo.cantidad_solicitada:
                    recibo.estado = estado
                
                # Guardar notas y condición de devolución
                recibo.notas_devolucion = request.POST.get('notas_devolucion', '')
                recibo.condicion_devolucion = request.POST.get('condicion_devolucion', '')
                
                # Establecer la fecha de devolución
                recibo.fecha_devolucion = timezone.now()
                
                # Guardar el recibo actualizado
                recibo.save()
                
                # Actualizar inventario para productos en buen estado
                if cantidad_buen_estado > 0:
                    try:
                        # Obtener una instancia fresca del producto
                        producto = Producto.objects.get(id_producto=recibo.producto.id_producto)
                        
                        # Debug información antes de devolver
                        previous_disponible = producto.cantidad_disponible
                        previous_en_renta = producto.cantidad_en_renta
                        
                        print(f"=== DEVOLUCIÓN MÚLTIPLE - {recibo.producto.nombre} ===")
                        print(f"Producto ID: {producto.id_producto}")
                        print(f"Cantidad total: {producto.cantidad_total()}")
                        print(f"En renta antes: {previous_en_renta}")
                        print(f"Disponible antes: {previous_disponible}")
                        print(f"Cantidad a devolver: {cantidad_buen_estado}")
                        
                        # Verificar que haya suficiente cantidad en renta
                        if cantidad_buen_estado <= producto.cantidad_en_renta:
                            # Flujo normal - tenemos suficientes en renta
                            producto.cantidad_en_renta -= cantidad_buen_estado
                            producto.cantidad_disponible += cantidad_buen_estado
                            producto.save()
                            
                            # Verificar que se haya guardado correctamente
                            producto_verificado = Producto.objects.get(id_producto=producto.id_producto)
                            
                            print(f"Devolución exitosa - Producto {producto.id_producto}")
                            print(f"Cantidad en renta después: {producto_verificado.cantidad_en_renta}")
                            print(f"Cantidad disponible después: {producto_verificado.cantidad_disponible}")
                            
                            # Actualizar contadores
                            total_buen_estado += cantidad_buen_estado
                        else:
                            # Corregimos inconsistencia: los productos deberían estar en renta pero no lo están
                            print(f"ADVERTENCIA: La cantidad a devolver ({cantidad_buen_estado}) excede la cantidad en renta ({producto.cantidad_en_renta})")
                            messages.warning(request, 
                                f"Inconsistencia detectada para '{producto.nombre}': La cantidad a devolver ({cantidad_buen_estado}) "
                                f"excede la cantidad en renta ({producto.cantidad_en_renta}). Se ha registrado la devolución pero el inventario puede estar inconsistente.")
                    
                    except Exception as e:
                        print(f"ERROR en devolución múltiple: {str(e)}")
                        messages.error(request, f"Error al procesar la devolución para '{recibo.producto.nombre}': {str(e)}")
                
                # Actualizar contadores totales
                total_danados += cantidad_danados
                total_inservibles += cantidad_inservibles
                recibos_actualizados += 1
            
            # Verificar si se actualizó algún recibo
            if recibos_actualizados == 0:
                messages.warning(request, "No se procesó ninguna devolución. Debes indicar al menos una cantidad para devolver.")
                return redirect('recibos:registrar_devolucion_multiple', pedido_id=pedido_id)
              # Verificar si todos los recibos del pedido han sido completamente devueltos
            todos_devueltos = not ReciboObra.objects.filter(
                pedido=pedido, 
                cantidad_vuelta__lt=F('cantidad_solicitada')
            ).exists()
            
            # Si todos los recibos están completados, actualizar el estado del pedido
            if todos_devueltos:
                pedido.estado_pedido_general = 'CERRADO'
                pedido.save()
                messages.info(request, "Se han devuelto todos los productos. El pedido ha sido marcado como CERRADO.")
            
            # Mostrar resumen de la operación
            messages.success(request, 
                f"Devolución múltiple registrada exitosamente. "
                f"Total devuelto: {total_buen_estado + total_danados + total_inservibles} "
                f"({total_buen_estado} en buen estado, {total_danados} dañados, {total_inservibles} inservibles)."
            )
            
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error al registrar la devolución múltiple: {str(e)}")
    
    return render(request, 'recibos/registrar_devolucion_multiple.html', {
        'pedido': pedido,
        'recibos_pendientes': recibos_pendientes,
    })

@login_required
@user_passes_test(puede_ver_recibos)
def crear_recibo_multiple(request, pedido_id):
    """Vista para crear recibos de obra para múltiples productos de un pedido"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        # Variables para llevar el conteo
        recibos_creados = 0
        productos_procesados = []
        errores = []
        
        condicion_general = request.POST.get('condicion_general', '')
        notas_generales = request.POST.get('notas_generales', '')
        
        # Procesar cada producto seleccionado
        for detalle in pedido.detalles.all():
            producto_id = detalle.producto.id_producto
            checkbox_name = f'seleccionado_{producto_id}'
            
            # Verificar si el producto fue seleccionado
            if checkbox_name in request.POST:
                cantidad_name = f'cantidad_{producto_id}'
                try:
                    cantidad = int(request.POST.get(cantidad_name, 1))
                    
                    # Validar que la cantidad sea válida
                    if cantidad <= 0:
                        errores.append(f"La cantidad para {detalle.producto.nombre} debe ser mayor a 0.")
                        continue
                    
                    if cantidad > detalle.cantidad:
                        errores.append(f"La cantidad para {detalle.producto.nombre} excede la disponible en el pedido.")
                        continue
                    
                    # Verificar inventario y corregir inconsistencias si es necesario
                    producto = detalle.producto
                    if producto.cantidad_en_renta < cantidad:
                        faltante = cantidad - producto.cantidad_en_renta
                        if producto.cantidad_disponible >= faltante:
                            # Movemos productos disponibles a en renta
                            producto.cantidad_disponible -= faltante
                            producto.cantidad_en_renta += faltante
                            producto.save()
                            print(f"Corregido: movidos {faltante} {producto.nombre} de disponible a en renta")
                        else:
                            errores.append(f"No hay suficientes {producto.nombre} disponibles o en renta.")
                            continue
                    
                    # Crear el recibo para este producto
                    recibo = ReciboObra.objects.create(
                        pedido=pedido,
                        cliente=pedido.cliente,
                        producto=producto,
                        detalle_pedido=detalle,
                        cantidad_solicitada=cantidad,
                        notas_entrega=notas_generales,
                        condicion_entrega=condicion_general,
                        empleado=request.user
                    )
                    
                    recibos_creados += 1
                    productos_procesados.append(producto.nombre)
                    
                except ValueError:
                    errores.append(f"Error al procesar la cantidad para {detalle.producto.nombre}.")
        
        # Mostrar mensajes según los resultados
        if recibos_creados > 0:
            productos_str = ", ".join(productos_procesados)
            messages.success(
                request, 
                f"Se han creado {recibos_creados} recibo(s) de obra exitosamente para: {productos_str}."
            )
            
            if errores:
                for error in errores:
                    messages.warning(request, error)
                
            # Si solo se creó un recibo, redirigir al PDF
            if recibos_creados == 1:
                ultimo_recibo = ReciboObra.objects.filter(pedido=pedido).order_by('-id').first()
                return redirect('recibos:generar_pdf', recibo_id=ultimo_recibo.id)
            else:
                return redirect('pedidos:detalle_pedido', pedido_id=pedido.id_pedido)
        else:
            if errores:
                for error in errores:
                    messages.error(request, error)
            else:
                messages.error(request, "No se seleccionó ningún producto para crear recibos.")
                
            return redirect('recibos:crear_recibo_multiple', pedido_id=pedido.id_pedido)
    
    # Renderizar formulario
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all(),
    }
    
    return render(request, 'recibos/crear_recibo_multiple.html', context)

@login_required
@user_passes_test(puede_ver_recibos)
def crear_recibo_consolidado(request, pedido_id):
    """Vista para crear un único recibo de obra con múltiples productos"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        # Variables para llevar el conteo
        productos_procesados = []
        errores = []
        
        condicion_general = request.POST.get('condicion_general', '')
        notas_generales = request.POST.get('notas_generales', '')
        
        # Verificar si hay al menos un producto seleccionado
        hay_productos = False
        for detalle in pedido.detalles.all():
            checkbox_name = f'seleccionado_{detalle.producto.id_producto}'
            if checkbox_name in request.POST:
                hay_productos = True
                break
                
        if not hay_productos:
            messages.error(request, "Debes seleccionar al menos un producto.")
            return redirect('recibos:crear_recibo_consolidado', pedido_id=pedido_id)
        
        # Crear el recibo principal
        recibo = ReciboObra.objects.create(
            pedido=pedido,
            cliente=pedido.cliente,
            cantidad_solicitada=0,  # Se actualizará después
            notas_entrega=notas_generales,
            condicion_entrega=condicion_general,
            empleado=request.user
        )
        
        cantidad_total = 0
        
        # Procesar cada producto seleccionado
        for detalle in pedido.detalles.all():
            producto_id = detalle.producto.id_producto
            checkbox_name = f'seleccionado_{producto_id}'
            
            # Verificar si el producto fue seleccionado
            if checkbox_name in request.POST:
                cantidad_name = f'cantidad_{producto_id}'
                try:
                    cantidad = int(request.POST.get(cantidad_name, 1))
                    
                    # Validar que la cantidad sea válida
                    if cantidad <= 0:
                        errores.append(f"La cantidad para {detalle.producto.nombre} debe ser mayor a 0.")
                        continue
                    
                    if cantidad > detalle.cantidad:
                        errores.append(f"La cantidad para {detalle.producto.nombre} excede la disponible en el pedido.")
                        continue
                    
                    # Verificar inventario y corregir inconsistencias si es necesario
                    producto = detalle.producto
                    if producto.cantidad_en_renta < cantidad:
                        faltante = cantidad - producto.cantidad_en_renta
                        if producto.cantidad_disponible >= faltante:
                            # Movemos productos disponibles a en renta
                            producto.cantidad_disponible -= faltante
                            producto.cantidad_en_renta += faltante
                            producto.save()
                            print(f"Corregido: movidos {faltante} {producto.nombre} de disponible a en renta")
                        else:
                            errores.append(f"No hay suficientes {producto.nombre} disponibles o en renta.")
                            continue
                    
                    # Crear el detalle del recibo para este producto
                    detalle_recibo = DetalleReciboObra.objects.create(
                        recibo=recibo,
                        producto=producto,
                        detalle_pedido=detalle,
                        cantidad_solicitada=cantidad,
                        condicion_entrega=condicion_general
                    )
                    
                    cantidad_total += cantidad
                    productos_procesados.append(producto.nombre)
                    
                except ValueError:
                    errores.append(f"Error al procesar la cantidad para {detalle.producto.nombre}.")
        
        # Actualizar la cantidad total en el recibo principal
        recibo.cantidad_solicitada = cantidad_total
        recibo.save()
        
        # Mostrar mensajes según los resultados
        if productos_procesados:
            productos_str = ", ".join(productos_procesados)
            messages.success(
                request, 
                f"Se ha creado un recibo de obra con los productos: {productos_str}."
            )
            
            if errores:
                for error in errores:
                    messages.warning(request, error)
                
            # Redireccionar a la lista de recibos en lugar de generar PDF
            return redirect('recibos:lista_recibos')
        else:
            # Si no se procesó ningún producto, eliminar el recibo
            recibo.delete()
            
            if errores:
                for error in errores:
                    messages.error(request, error)
            else:
                messages.error(request, "No se pudo crear el recibo. Verifica la selección de productos.")
                
            return redirect('recibos:crear_recibo_consolidado', pedido_id=pedido_id)
    
    # Renderizar formulario
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all(),
    }
    
    return render(request, 'recibos/crear_recibo_consolidado.html', context)

@login_required
def generar_pdf_consolidado(request, recibo_id):
    """Vista para generar el PDF del recibo de obra consolidado"""
    recibo = get_object_or_404(ReciboObra, id=recibo_id)
    
    # Buffer para almacenar el PDF
    buffer = io.BytesIO()
    
    # Crear el objeto PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Configuración de la fuente
    p.setFont("Helvetica-Bold", 16)
    
    # Título
    p.drawCentredString(width / 2, height - 50, "RECIBO DE OBRA CONSOLIDADO")
    
    # Logo - si está disponible
    try:
        p.drawImage("static/logo_multiandamios.png", 40, height - 80, width=100, height=70)
    except:
        pass
    
    # Información del recibo
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 120, f"Recibo Nro: {recibo.id}")
    p.drawString(40, height - 140, f"Fecha: {recibo.fecha_entrega.strftime('%d/%m/%Y %H:%M')}")
    
    # Información del cliente y pedido
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 170, f"Cliente: {recibo.cliente.usuario.get_full_name()}")
    p.drawString(40, height - 190, f"Pedido: #{recibo.pedido.id_pedido}")
    p.drawString(40, height - 210, f"Dirección: {recibo.pedido.direccion_entrega}")
    
    # Tabla de productos
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 240, "PRODUCTOS ENTREGADOS:")
    
    p.setFont("Helvetica", 10)
    headers = ["Producto", "Cantidad", "Estado"]
    data = []
    
    # Encabezados de tabla
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, height - 260, headers[0])
    p.drawString(300, height - 260, headers[1])
    p.drawString(400, height - 260, headers[2])
    
    # Datos de la tabla
    p.setFont("Helvetica", 10)
    y_position = height - 280
    
    for i, detalle in enumerate(recibo.detalles.all()):
        # Alternar colores para mejorar legibilidad
        if i % 2 == 0:
            p.setFillColor(colors.lightgrey)
            p.rect(40, y_position - 15, width - 80, 20, fill=True)
            p.setFillColor(colors.black)
        
        p.drawString(50, y_position, detalle.producto.nombre)
        p.drawString(300, y_position, str(detalle.cantidad_solicitada))
        p.drawString(400, y_position, recibo.get_estado_display())
        
        y_position -= 20
        
        # Si ya no cabe en la página, crear una nueva
        if y_position < 100:
            p.showPage()
            p.setFont("Helvetica-Bold", 12)
            p.drawString(40, height - 50, "RECIBO DE OBRA (Continuación)")
            p.setFont("Helvetica", 10)
            y_position = height - 80
    
    # Saltar 20 puntos
    y_position -= 20
    
    # Condición del equipo
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y_position, "Condición del Equipo:")
    p.setFont("Helvetica", 10)
    
    # Dividir texto largo en varias líneas si es necesario
    texto_condicion = recibo.condicion_entrega if recibo.condicion_entrega else ""
    max_width = width - 80
    
    # Bajar 15 puntos para el texto de condición
    y_position -= 15
    
    for line in texto_condicion.split('\n'):
        while line and y_position > 50:
            if p.stringWidth(line, "Helvetica", 10) <= max_width:
                p.drawString(40, y_position, line)
                y_position -= 15
                line = ""
            else:
                # Buscar punto de corte
                cut_point = len(line)
                while p.stringWidth(line[:cut_point], "Helvetica", 10) > max_width:
                    cut_point -= 1
                
                p.drawString(40, y_position, line[:cut_point])
                y_position -= 15
                line = line[cut_point:].strip()
    
    # Notas adicionales
    y_position -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y_position, "Notas Adicionales:")
    p.setFont("Helvetica", 10)
    
    # Bajar 15 puntos para el texto de notas
    y_position -= 15
    
    # Dividir texto largo en varias líneas si es necesario
    texto_notas = recibo.notas_entrega if recibo.notas_entrega else ""
    
    for line in texto_notas.split('\n'):
        while line and y_position > 50:
            if p.stringWidth(line, "Helvetica", 10) <= max_width:
                p.drawString(40, y_position, line)
                y_position -= 15
                line = ""
            else:
                # Buscar punto de corte
                cut_point = len(line)
                while p.stringWidth(line[:cut_point], "Helvetica", 10) > max_width:
                    cut_point -= 1
                
                p.drawString(40, y_position, line[:cut_point])
                y_position -= 15
                line = line[cut_point:].strip()
    
    # Firmas
    y_position = min(y_position, 100)  # Asegurar que quede espacio para firmas
    
    p.line(100, y_position - 30, 250, y_position - 30)
    p.drawCentredString(175, y_position - 45, "Firma del Empleado")
    p.drawCentredString(175, y_position - 60, recibo.empleado.get_full_name())
    
    p.line(350, y_position - 30, 500, y_position - 30)
    p.drawCentredString(425, y_position - 45, "Firma del Cliente")
    p.drawCentredString(425, y_position - 60, recibo.cliente.usuario.get_full_name())
    
    # Guardar el PDF
    p.showPage()
    p.save()
    
    # Preparar la respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recibo_obra_{recibo.id}.pdf"'
    
    return response

@login_required
@user_passes_test(puede_ver_recibos)
def registrar_devolucion_consolidado(request, recibo_id):
    """Vista para registrar la devolución de equipos de un recibo consolidado"""
    recibo = get_object_or_404(ReciboObra, id=recibo_id)
    detalles = recibo.detalles.all()
    
    if not detalles.exists():
        messages.error(request, "Este recibo no tiene detalles asociados.")
        return redirect('recibos:lista_recibos')
    
    if request.method == 'POST':
        errores = []
        productos_procesados = []
        cantidad_total_devuelta = 0
        
        estado = request.POST.get('estado')
        notas_devolucion = request.POST.get('notas_devolucion', '')
        condicion_devolucion = request.POST.get('condicion_devolucion', '')
        
        # Procesar cada detalle del recibo
        for detalle in detalles:
            buen_estado = int(request.POST.get(f'buen_estado_{detalle.id}', 0))
            danados = int(request.POST.get(f'danados_{detalle.id}', 0))
            inservibles = int(request.POST.get(f'inservibles_{detalle.id}', 0))
            
            total_devuelto = buen_estado + danados + inservibles
            
            if total_devuelto > 0:
                # Validar que la cantidad total no exceda la pendiente
                if total_devuelto > detalle.cantidad_pendiente:
                    errores.append(f"La cantidad devuelta para {detalle.producto.nombre} excede la pendiente.")
                    continue
                    
                # Actualizar el detalle del recibo
                detalle.cantidad_buen_estado += buen_estado
                detalle.cantidad_danados += danados
                detalle.cantidad_inservibles += inservibles
                detalle.cantidad_vuelta += total_devuelto
                detalle.save()
                
                cantidad_total_devuelta += total_devuelto
                productos_procesados.append(detalle.producto.nombre)
                
                # Devolver al inventario los productos en buen estado
                if buen_estado > 0:
                    try:
                        producto = detalle.producto
                        
                        # Verificar que haya suficientes en renta
                        if producto.cantidad_en_renta >= buen_estado:
                            producto.cantidad_en_renta -= buen_estado
                            producto.cantidad_disponible += buen_estado
                            producto.save()
                            print(f"Devueltos {buen_estado} {producto.nombre} al inventario")
                        else:
                            print(f"ADVERTENCIA: No hay suficientes {producto.nombre} en renta")
                            errores.append(f"No hay suficientes {producto.nombre} en renta para devolver.")
                    except Exception as e:
                        print(f"ERROR en devolución: {str(e)}")
                        errores.append(f"Error al procesar la devolución de {detalle.producto.nombre}: {str(e)}")
        
        # Actualizar el recibo principal si se procesó algún producto
        if productos_procesados:
            recibo.cantidad_vuelta += cantidad_total_devuelta
            recibo.estado = estado
            recibo.notas_devolucion = notas_devolucion
            recibo.condicion_devolucion = condicion_devolucion
            recibo.fecha_devolucion = timezone.now()
            recibo.save()
            
            # Mostrar mensajes de éxito y errores
            productos_str = ", ".join(productos_procesados)
            messages.success(request, f"Se ha registrado la devolución de: {productos_str}.")
            
            if errores:
                for error in errores:
                    messages.warning(request, error)
            
            # Verificar si el recibo está completo para cerrar el pedido
            if recibo.cantidad_vuelta >= recibo.cantidad_solicitada:
                # Verificar si todos los detalles están completos
                todos_completos = all(detalle.cantidad_vuelta == detalle.cantidad_solicitada for detalle in detalles)
                
                if todos_completos:
                    recibo.pedido.estado_pedido_general = 'CERRADO'
                    recibo.pedido.save()
                    messages.info(request, "El pedido ha sido marcado como CERRADO.")
            
            return redirect('recibos:lista_recibos')
        else:
            messages.error(request, "No se registró ninguna devolución. Verifica los datos ingresados.")
            
            if errores:
                for error in errores:
                    messages.error(request, error)
    
    # Preparar estado para el template
    estados = ReciboObra.ESTADO_CHOICES
    
    return render(request, 'recibos/registrar_devolucion_consolidado.html', {
        'recibo': recibo,
        'detalles': detalles,
        'estados': estados
    })
