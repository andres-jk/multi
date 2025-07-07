from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
from .models import ReciboObra, DetalleReciboObra, EstadoProductoIndividual
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
                    Q(detalles__producto__nombre__icontains=search_query)
                ).distinct()
        except ValueError:
            # Si no es un número, buscar por nombre de cliente o producto
            from django.db.models import Q
            recibos = recibos.filter(
                Q(cliente__usuario__first_name__icontains=search_query) |
                Q(cliente__usuario__last_name__icontains=search_query) |
                Q(detalles__producto__nombre__icontains=search_query)
            ).distinct()
    
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
            
            # Crear el recibo principal
            recibo = ReciboObra.objects.create(
                pedido=pedido,
                cliente=pedido.cliente,
                notas_entrega=notas,
                condicion_entrega=condicion,
                empleado=request.user
            )
            
            # Crear el detalle del recibo para el producto seleccionado
            detalle_pedido = pedido.detalles.filter(producto_id=producto_id).first()
            if detalle_pedido:
                DetalleReciboObra.objects.create(
                    recibo=recibo,
                    producto_id=producto_id,
                    detalle_pedido=detalle_pedido,
                    cantidad_solicitada=cantidad,
                    estado='PENDIENTE'
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
    
    # Obtener el primer detalle para compatibilidad con recibos simples
    detalle_principal = recibo.detalles.first()
    
    if not detalle_principal:
        messages.error(request, "Este recibo no tiene detalles asociados.")
        return redirect('recibos:lista_recibos')
    
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
            cantidad_pendiente = detalle_principal.cantidad_pendiente
            if cantidad_total > cantidad_pendiente:
                raise ValueError(f"La cantidad total devuelta ({cantidad_total}) no puede ser mayor a la cantidad pendiente ({cantidad_pendiente}).")
            
            # Actualizar el detalle del recibo
            detalle_principal.cantidad_buen_estado += cantidad_buen_estado
            detalle_principal.cantidad_danados += cantidad_danados
            detalle_principal.cantidad_inservibles += cantidad_inservibles
            detalle_principal.cantidad_vuelta += cantidad_total
            detalle_principal.estado = estado
            detalle_principal.save()
            
            # Actualizar el recibo principal
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
                    
                    # Logging detallado para depuración
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"=== DEVOLUCIÓN DE PRODUCTOS ===")
                    logger.info(f"Producto ID: {producto_id}")
                    logger.info(f"Producto Nombre: {producto_actualizado.nombre}")
                    logger.info(f"Cantidad total del producto: {producto_actualizado.cantidad_total()}")
                    logger.info(f"Cantidad en renta antes: {previous_en_renta}")
                    logger.info(f"Cantidad disponible antes: {previous_disponible}")
                    logger.info(f"Cantidad reservada antes: {previous_reservada}")
                    logger.info(f"Cantidad a devolver: {cantidad_buen_estado}")
                    
                    # Verificar que haya suficiente cantidad en renta
                    if cantidad_buen_estado <= producto_actualizado.cantidad_en_renta:
                        # Flujo normal - tenemos suficientes en renta
                        from django.db import transaction
                        
                        try:
                            with transaction.atomic():
                                if producto_actualizado.devolver_de_renta(cantidad_buen_estado):
                                    # Verificar que se haya guardado correctamente
                                    producto_verificado = Producto.objects.get(id_producto=producto_id)
                                    
                                    logger.info(f"Devolución exitosa - Producto {producto_id}")
                                    logger.info(f"Cantidad en renta después: {producto_verificado.cantidad_en_renta}")
                                    logger.info(f"Cantidad disponible después: {producto_verificado.cantidad_disponible}")
                                    logger.info(f"=== FIN DEVOLUCIÓN EXITOSA ===")
                                    
                                    messages.success(request,
                                        f"✅ Se han devuelto {cantidad_buen_estado} unidades en buen estado al inventario. "
                                        f"Disponibles: {previous_disponible} → {producto_verificado.cantidad_disponible}. "
                                        f"En renta: {previous_en_renta} → {producto_verificado.cantidad_en_renta}.")
                                else:
                                    raise Exception("El método devolver_de_renta retornó False")
                        except Exception as txn_error:
                            logger.error(f"ERROR en transacción de devolución: {str(txn_error)}")
                            messages.error(request, f"Error al devolver {cantidad_buen_estado} productos al inventario: {str(txn_error)}")
                    else:
                        # Caso especial: no hay suficientes productos en renta
                        logger.warning(f"Productos insuficientes en renta: {cantidad_buen_estado} > {producto_actualizado.cantidad_en_renta}")
                        
                        # Verificar si ya están disponibles (posible inconsistencia de datos)
                        if producto_actualizado.cantidad_disponible >= cantidad_buen_estado:
                            # Los productos ya están disponibles, solo registramos la devolución
                            logger.info(f"Los productos ya están disponibles, solo registrando la devolución en el recibo")
                            messages.info(request,
                                f"⚠️ Los productos ya estaban disponibles en el inventario. Solo se ha registrado la devolución.")
                        else:
                            # Error: no hay suficientes productos en ningún estado
                            total_disponible = producto_actualizado.cantidad_disponible + producto_actualizado.cantidad_en_renta
                            logger.error(f"Error crítico: Cantidad a devolver ({cantidad_buen_estado}) excede el total disponible ({total_disponible})")
                            
                            messages.error(request, 
                                f"❌ Error crítico: No se pudieron devolver los productos al inventario. "
                                f"Cantidad a devolver: {cantidad_buen_estado}, "
                                f"En renta: {producto_actualizado.cantidad_en_renta}, "
                                f"Disponible: {producto_actualizado.cantidad_disponible}")
                            
                            # Enviar notificación al administrador
                            logger.critical(f"INCONSISTENCIA DE INVENTARIO - Recibo #{recibo.id}, Producto {producto_actualizado.nombre}")
                            
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"ERROR GENERAL en devolución: {str(e)}")
                    logger.error(f"Recibo: {recibo.id}, Producto: {recibo.producto.nombre if recibo.producto else 'N/A'}")
                    messages.error(request, f"Error inesperado al procesar la devolución: {str(e)}")
                    
                    # En caso de error crítico, no fallar completamente
                    # Solo registrar el error pero permitir continuar con el resto del proceso
            
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
@user_passes_test(puede_ver_recibos)
def administrar_productos_individuales(request, recibo_id):
    """Vista para administrar el estado individual de cada producto en un recibo de obra"""
    recibo = get_object_or_404(ReciboObra, id=recibo_id)
    detalles = recibo.detalles.all()
    
    # Verificar si la tabla EstadoProductoIndividual existe
    tabla_existe = True
    try:
        # Probar una consulta simple para verificar que la tabla existe
        list(EstadoProductoIndividual.objects.all()[:1])  # Forzar evaluación de la consulta
    except Exception as e:
        tabla_existe = False
        print(f"Tabla no existe, intentando crearla: {e}")
        
        # Intentar crear la tabla automáticamente
        if crear_tabla_estado_individual():
            print("Tabla creada exitosamente, verificando nuevamente...")
            try:
                list(EstadoProductoIndividual.objects.all()[:1])
                tabla_existe = True
                print("Tabla ahora accesible")
            except Exception as e2:
                print(f"Tabla creada pero aún no accesible: {e2}")
                tabla_existe = False
        
        if not tabla_existe and request.method == 'POST':
            messages.error(request, 
                "Error: La tabla de estados individuales no existe y no se pudo crear automáticamente. "
                "Por favor, contacta al administrador para aplicar las migraciones necesarias."
            )
            return redirect('recibos:lista_recibos')
    
    if request.method == 'POST':
        try:
            # Procesar el formulario de estado de productos
            for detalle in detalles:
                # Crear estados individuales para cada producto si no existen
                for i in range(detalle.cantidad_solicitada):
                    estado_key = f'estado_{detalle.id}_{i}'
                    observaciones_key = f'observaciones_{detalle.id}_{i}'
                    numero_serie_key = f'numero_serie_{detalle.id}_{i}'
                    
                    if estado_key in request.POST:
                        estado_valor = request.POST[estado_key]
                        observaciones = request.POST.get(observaciones_key, '')
                        numero_serie = request.POST.get(numero_serie_key, '')
                        
                        # Buscar o crear el estado individual
                        estado_individual, created = EstadoProductoIndividual.objects.get_or_create(
                            detalle_recibo=detalle,
                            numero_serie=numero_serie or f"Item-{i+1}",
                            defaults={
                                'estado': estado_valor,
                                'observaciones': observaciones,
                                'revisado_por': request.user,
                            }
                        )
                    
                    if not created:
                        # Actualizar estado existente
                        estado_individual.estado = estado_valor
                        estado_individual.observaciones = observaciones
                        estado_individual.revisado_por = request.user
                        estado_individual.fecha_revision = timezone.now()
                        estado_individual.save()
        
            messages.success(request, 'Estados de productos actualizados exitosamente.')
            return redirect('recibos:administrar_productos_individuales', recibo_id=recibo_id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar estados de productos: {str(e)}')
            return redirect('recibos:lista_recibos')
    
    # Preparar datos para la plantilla
    productos_data = []
    for detalle in detalles:
        estados_existentes = []
        if tabla_existe:
            try:
                estados_existentes = EstadoProductoIndividual.objects.filter(detalle_recibo=detalle)
                # Forzar evaluación del QuerySet para verificar que la tabla realmente existe
                list(estados_existentes)
            except Exception as e:
                # Si la tabla no existe, usar lista vacía y marcar tabla como no existente
                estados_existentes = []
                tabla_existe = False
                print(f"Error al acceder a EstadoProductoIndividual: {e}")  # Para debug
        
        # Crear lista de productos individuales
        productos_individuales = []
        for i in range(detalle.cantidad_solicitada):
            # Buscar estado existente o crear uno por defecto
            estado_individual = None
            if tabla_existe:
                try:
                    # Solo evaluar si la tabla existe
                    if estados_existentes:  # Esto puede ser una lista o QuerySet
                        for estado in estados_existentes:
                            if estado.numero_serie == f"Item-{i+1}":
                                estado_individual = estado
                                break
                except Exception:
                    estado_individual = None
            
            productos_individuales.append({
                'index': i,
                'numero_serie': f"Item-{i+1}",
                'estado_individual': estado_individual,
            })
        
        productos_data.append({
            'detalle': detalle,
            'productos_individuales': productos_individuales,
        })
    
    # Obtener opciones de estado
    if tabla_existe:
        estados_choices = EstadoProductoIndividual.ESTADO_CHOICES
    else:
        estados_choices = [
            ('BUEN_ESTADO', 'Buen Estado'),
            ('PARA_REPARACION', 'Para Reparación'),
            ('INUTILIZABLE', 'Inutilizable'),
        ]
    
    context = {
        'recibo': recibo,
        'productos_data': productos_data,
        'estados_choices': estados_choices,
        'tabla_existe': tabla_existe,
    }
    
    return render(request, 'recibos/administrar_productos_individuales.html', context)

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
    recibos = ReciboObra.objects.prefetch_related('detalles').all()
    recibos_count = recibos.count()
    
    recibos_pendientes = 0
    recibos_en_uso = 0
    recibos_devueltos = 0

    for recibo in recibos:
        estado = recibo.estado_general
        if estado == 'PENDIENTE':
            recibos_pendientes += 1
        elif estado == 'EN_USO':
            recibos_en_uso += 1
        elif estado == 'DEVUELTO':
            recibos_devueltos += 1

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
                    
                    # Buscar un recibo existente para este pedido o crear uno nuevo
                    recibo, created = ReciboObra.objects.get_or_create(
                        pedido=pedido,
                        defaults={
                            'cliente': pedido.cliente,
                            'notas_entrega': notas_generales,
                            'condicion_entrega': condicion_general,
                            'empleado': request.user
                        }
                    )
                    
                    # Crear el detalle del recibo para este producto
                    DetalleReciboObra.objects.create(
                        recibo=recibo,
                        producto=producto,
                        detalle_pedido=detalle,
                        cantidad_solicitada=cantidad,
                        estado='PENDIENTE'
                    )
                    
                    if created:
                        recibos_creados += 1
                    productos_procesados.append(producto.nombre)
                    
                except ValueError:
                    errores.append(f"Error al procesar la cantidad para {detalle.producto.nombre}.")
        
        # Mostrar mensajes según los resultados
        if productos_procesados:
            productos_str = ", ".join(productos_procesados)
            messages.success(
                request, 
                f"Se han agregado productos al recibo de obra exitosamente: {productos_str}."
            )
            
            if errores:
                for error in errores:
                    messages.warning(request, error)
                
            # Redirigir al recibo (siempre habrá uno para este pedido)
            recibo = ReciboObra.objects.filter(pedido=pedido).order_by('-id').first()
            if recibo:
                return redirect('recibos:generar_pdf', recibo_id=recibo.id)
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
    
    # Determinar si es un recibo para devolución
    es_devolucion = pedido.estado_pedido_general == 'programado_devolucion'
    
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
            notas_entrega=notas_generales,
            condicion_entrega=condicion_general,
            empleado=request.user,
            es_recibo_devolucion=es_devolucion
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
                        cantidad_solicitada=cantidad
                    )
                    
                    cantidad_total += cantidad
                    productos_procesados.append(producto.nombre)
                    
                except ValueError:
                    errores.append(f"Error al procesar la cantidad para {detalle.producto.nombre}.")
        
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
        'es_devolucion': es_devolucion,
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
                        
                        # Obtener estado actual para logging
                        previous_disponible = producto.cantidad_disponible
                        previous_en_renta = producto.cantidad_en_renta
                        
                        # Logging detallado
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"=== DEVOLUCIÓN CONSOLIDADA ===")
                        logger.info(f"Producto: {producto.nombre}")
                        logger.info(f"Estado antes - En renta: {previous_en_renta}, Disponible: {previous_disponible}")
                        logger.info(f"Cantidad a devolver: {buen_estado}")
                        
                        # Usar el método del modelo para manejar la devolución correctamente
                        from django.db import transaction
                        
                        try:
                            with transaction.atomic():
                                if producto.devolver_de_renta(buen_estado):
                                    # Verificar cambio
                                    producto.refresh_from_db()
                                    logger.info(f"✅ Devolución exitosa - En renta: {previous_en_renta} → {producto.cantidad_en_renta}")
                                    logger.info(f"Disponible: {previous_disponible} → {producto.cantidad_disponible}")
                                    logger.info(f"=== FIN DEVOLUCIÓN CONSOLIDADA EXITOSA ===")
                                else:
                                    raise Exception(f"No hay suficientes {producto.nombre} en renta para devolver {buen_estado} unidades")
                        except Exception as txn_error:
                            logger.error(f"ERROR en devolución consolidada: {str(txn_error)}")
                            errores.append(f"Error al devolver {producto.nombre}: {str(txn_error)}")
                            
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"ERROR GENERAL en devolución consolidada: {str(e)}")
                        errores.append(f"Error inesperado al procesar la devolución de {detalle.producto.nombre}: {str(e)}")
        
        # Actualizar el recibo principal si se procesó algún producto
        if productos_procesados:
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
            
            # Verificar si todos los detalles están completos para cerrar el pedido
            todos_completos = all(detalle.esta_completo for detalle in detalles)
                
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
    
    return render(request, 'recibos/registrar_devolucion_consolidado.html', {
        'recibo': recibo,
        'detalles': detalles,
    })

def crear_tabla_estado_individual():
    """Crear la tabla EstadoProductoIndividual si no existe"""
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS "recibos_estadoproductoindividual" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "numero_serie" varchar(100),
                    "estado" varchar(20) NOT NULL DEFAULT 'BUEN_ESTADO',
                    "observaciones" text,
                    "fecha_revision" datetime NOT NULL,
                    "detalle_recibo_id" bigint NOT NULL,
                    "revisado_por_id" integer,
                    FOREIGN KEY ("detalle_recibo_id") REFERENCES "recibos_detallereciboobra" ("id") DEFERRABLE INITIALLY DEFERRED,
                    FOREIGN KEY ("revisado_por_id") REFERENCES "usuarios_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
                );
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_detalle_recibo_id_a8e0de9c" ON "recibos_estadoproductoindividual" ("detalle_recibo_id");')
            cursor.execute('CREATE INDEX IF NOT EXISTS "recibos_estadoproductoindividual_revisado_por_id_12345678" ON "recibos_estadoproductoindividual" ("revisado_por_id");')
            cursor.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('recibos', '0003_estadoproductoindividual', datetime('now'));")
        return True
    except Exception as e:
        print(f"Error creando tabla: {e}")
        return False

@login_required
@user_passes_test(es_staff)
def diagnostico_devoluciones(request):
    """Vista para diagnosticar problemas de devolución"""
    from django.db.models import F, Sum
    
    # Obtener información de productos
    productos_con_renta = Producto.objects.filter(cantidad_en_renta__gt=0)
    
    # Obtener recibos que tienen detalles pendientes
    recibos_con_pendientes = ReciboObra.objects.filter(
        detalles__cantidad_vuelta__lt=F('detalles__cantidad_solicitada')
    ).distinct()
    
    # Obtener detalles pendientes directamente
    detalles_pendientes = DetalleReciboObra.objects.filter(cantidad_vuelta__lt=F('cantidad_solicitada'))
    
    # Verificar inconsistencias
    inconsistencias = []
    
    # Para recibos con detalles pendientes, verificar cada detalle
    for recibo in recibos_con_pendientes:
        for detalle in recibo.detalles.filter(cantidad_vuelta__lt=F('cantidad_solicitada')):
            pendiente = detalle.cantidad_solicitada - detalle.cantidad_vuelta
            if detalle.producto and pendiente > detalle.producto.cantidad_en_renta:
                inconsistencias.append({
                    'tipo': 'detalle_pendiente',
                    'objeto': detalle,
                    'recibo': recibo,
                    'pendiente': pendiente,
                    'en_renta': detalle.producto.cantidad_en_renta,
                    'producto': detalle.producto
                })
    
    # También verificar detalles independientemente para una vista completa
    detalles_con_problemas = []
    for detalle in detalles_pendientes:
        pendiente = detalle.cantidad_solicitada - detalle.cantidad_vuelta
        if detalle.producto and pendiente > detalle.producto.cantidad_en_renta:
            detalles_con_problemas.append({
                'detalle': detalle,
                'pendiente': pendiente,
                'en_renta': detalle.producto.cantidad_en_renta,
                'producto': detalle.producto
            })
    
    context = {
        'productos_con_renta': productos_con_renta,
        'recibos_con_pendientes': recibos_con_pendientes,
        'detalles_pendientes': detalles_pendientes,
        'inconsistencias': inconsistencias,
        'detalles_con_problemas': detalles_con_problemas,
        'total_problemas': len(recibos_con_pendientes),
        'total_detalles_pendientes': len(detalles_pendientes),
        'total_inconsistencias': len(inconsistencias),
    }
    
    return render(request, 'recibos/diagnostico_devoluciones.html', context)
