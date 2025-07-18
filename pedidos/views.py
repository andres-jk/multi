from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db import transaction, IntegrityError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from decimal import Decimal
import io
import os
from datetime import datetime
from .models import Pedido, DetallePedido
from usuarios.models import Cliente, Usuario
from productos.models import Producto
from django.db.models import Q
from usuarios.forms import ClienteForm, ClienteCompletoForm, ClienteCompletoForm

def es_staff(user):
    """Verifica si un usuario es staff, admin o empleado"""
    return user.is_staff or user.rol in ['admin', 'empleado']

def es_cliente(user):
    """Verifica si un usuario es cliente (no admin ni empleado)"""
    return user.rol == 'cliente' and not user.is_staff

@login_required
@user_passes_test(es_staff)
def lista_clientes(request):
    busqueda = request.GET.get('busqueda_identidad', '').strip()
    estado_filtro = request.GET.get('estado', '')
    rol_filtro = request.GET.get('rol', '')
    
    clientes = Cliente.objects.select_related('usuario').all()
    
    # Filtro por búsqueda
    if busqueda:
        clientes = clientes.filter(
            Q(usuario__numero_identidad__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda) |
            Q(usuario__last_name__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda) |
            Q(usuario__email__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(direccion__icontains=busqueda)
        )
    
    # Filtro por estado
    if estado_filtro == 'activo':
        clientes = clientes.filter(usuario__is_active=True)
    elif estado_filtro == 'inactivo':
        clientes = clientes.filter(usuario__is_active=False)
    
    # Filtro por rol
    if rol_filtro:
        clientes = clientes.filter(usuario__rol=rol_filtro)
    
    # Opciones para los filtros
    estados = [
        ('', 'Todos los estados'),
        ('activo', 'Activos'),
        ('inactivo', 'Inactivos'),
    ]
    
    roles = [('', 'Todos los roles')] + list(Usuario.ROLES)
    
    context = {
        'clientes': clientes,
        'busqueda': busqueda,
        'estado_filtro': estado_filtro,
        'rol_filtro': rol_filtro,
        'estados': estados,
        'roles': roles,
    }
    
    return render(request, 'pedidos/lista_clientes.html', context)

@login_required
@user_passes_test(es_staff)
def lista_pedidos(request):
    """Vista para listar todos los pedidos"""
    pedidos = Pedido.objects.all().select_related('cliente__usuario').order_by('-fecha')
    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(es_staff)
def admin_productos(request):
    
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio_diario = request.POST.get('precio_diario')
            dias_minimos_renta = request.POST.get('dias_minimos_renta')
            peso = request.POST.get('peso')
            cantidad = request.POST.get('cantidad')
            imagen = request.FILES.get('imagen')
            
            # Validar y convertir valores numéricos
            try:
                precio_diario_decimal = Decimal(precio_diario) if precio_diario else Decimal('0')
                dias_minimos_int = int(dias_minimos_renta) if dias_minimos_renta else 1
                peso_decimal = Decimal(peso) if peso else Decimal('0')
                cantidad_int = int(cantidad) if cantidad else 0
            except (ValueError, TypeError):
                messages.error(request, 'Error en los valores numéricos. Verifique precio diario, días mínimos, peso y cantidad.')
                return redirect('pedidos:admin_productos')
            
            # Validar días mínimos
            if dias_minimos_int < 1:
                dias_minimos_int = 1
                messages.warning(request, 'Días mínimos de renta debe ser al menos 1. Se ha ajustado automáticamente.')
            
            # Crear el producto
            producto_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'precio_diario': precio_diario_decimal,
                'dias_minimos_renta': dias_minimos_int,
                'peso': peso_decimal,
                'cantidad_disponible': cantidad_int,
                'imagen': imagen
            }
            
            Producto.objects.create(**producto_data)
            messages.success(request, f'Producto "{nombre}" creado exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
        
        return redirect('pedidos:admin_productos')
        
    return render(request, 'pedidos/admin_productos.html', {'productos': productos})

@login_required
@user_passes_test(es_staff)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio_diario = request.POST.get('precio_diario')
            dias_minimos_renta = request.POST.get('dias_minimos_renta')
            cantidad = request.POST.get('cantidad')
            peso = request.POST.get('peso', producto.peso)
            
            # Validar valores numéricos
            precio_diario_decimal = Decimal(precio_diario) if precio_diario else producto.precio_diario
            dias_minimos_int = max(1, int(dias_minimos_renta)) if dias_minimos_renta else producto.dias_minimos_renta
            cantidad_int = int(cantidad) if cantidad else producto.cantidad_disponible
            peso_decimal = Decimal(peso) if peso else producto.peso
            
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.precio_diario = precio_diario_decimal
            producto.dias_minimos_renta = dias_minimos_int
            producto.cantidad_disponible = cantidad_int
            producto.peso = peso_decimal
            
            if request.FILES.get('imagen'):
                producto.imagen = request.FILES.get('imagen')
            
            producto.save()
            messages.success(request, f'Producto "{nombre}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
        
        return redirect('pedidos:admin_productos')
        
    return render(request, 'pedidos/editar_producto.html', {'producto': producto})

@login_required
@user_passes_test(es_staff)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    producto.delete()
    return redirect('pedidos:admin_productos')# Verificar si el usuario es cliente, si es así, redirigir a inicio
    if request.user.rol == 'cliente':
        messages.error(request, "No tienes permisos para acceder a la sección de pedidos.")
        return redirect('usuarios:inicio_cliente')
        
    

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        with transaction.atomic():
            try:
                carrito = request.session.get('carrito', {})
                if not carrito:
                    messages.error(request, 'El carrito está vacío')
                    return redirect('usuarios:carrito')  # Corregido: usar la URL correcta
                
                # Asegurar que el usuario tenga un cliente asociado
                cliente, created = Cliente.objects.get_or_create(
                    usuario=request.user,
                    defaults={
                        'telefono': getattr(request.user, 'telefono', ''),
                        'direccion': request.POST.get('direccion_entrega', getattr(request.user, 'direccion', ''))
                    }
                )
                
                # Crear el pedido
                pedido = Pedido.objects.create(
                    cliente=cliente,
                    direccion_entrega=request.POST.get('direccion_entrega'),
                    notas=request.POST.get('notas', '')
                )
                
                # Crear los detalles del pedido
                for key, item in carrito.items():
                    producto = Producto.objects.get(id_producto=int(key))
                    detalle_pedido = DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=item['cantidad'],
                        dias_renta=item.get('dias', item.get('meses', 1)),  # Support both old and new format
                        precio_diario=item.get('precio_diario', item.get('precio_unitario', 0))
                    )
                    
                    # Mover productos de reservados a en renta
                    if not producto.confirmar_renta(item['cantidad']):
                        raise Exception(f'No hay suficiente stock para {producto.nombre}')

                    # Crear recibo de obra automáticamente para cada producto
                    try:
                        from recibos.models import ReciboObra
                        
                        recibo = ReciboObra.objects.create(
                            pedido=pedido,
                            cliente=cliente,
                            producto=producto,
                            detalle_pedido=detalle_pedido,
                            cantidad_solicitada=item['cantidad'],
                            notas_entrega=f"Recibo generado automáticamente para el pedido #{pedido.id_pedido}",
                            condicion_entrega="Equipo en buen estado al momento de la entrega",
                            empleado=request.user if hasattr(request.user, 'rol') and request.user.rol in ['admin', 'empleado', 'recibos_obra'] else None,
                            estado='EN_USO'
                        )
                        messages.success(request, f"Recibo de obra #{recibo.id} creado automáticamente para {producto.nombre}")
                    except ImportError:
                        messages.warning(request, f"No se pudo importar el modelo ReciboObra")
                    except Exception as e:
                        messages.warning(request, f"No se pudo crear el recibo de obra para {producto.nombre}: {str(e)}")
                
                # Limpiar el carrito
                del request.session['carrito']
                request.session.modified = True
                messages.success(request, f'Pedido #{pedido.id_pedido} creado exitosamente')
                
                return redirect('usuarios:confirmacion_pago', pedido_id=pedido.id_pedido)
                
            except Producto.DoesNotExist:
                messages.error(request, 'Error: Uno de los productos en el carrito no fue encontrado.')
                return redirect('usuarios:carrito')
            except Exception as e:
                messages.error(request, f'Error al crear el pedido: {str(e)}')
                return redirect('usuarios:carrito')

@login_required
@user_passes_test(es_staff)
def detalle_pedido(request, pedido_id):
    """Vista para que empleados/admin vean el detalle de un pedido y gestionen pagos"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Obtener recibos de obra asociados a este pedido
    from recibos.models import ReciboObra
    recibos = ReciboObra.objects.filter(pedido=pedido)
    
    # Obtener información de pago
    from usuarios.models import MetodoPago
    pagos = MetodoPago.objects.filter(pedido=pedido).order_by('-fecha_creacion')
    pago_pendiente = pagos.filter(estado='pendiente').first()
    
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all(),
        'recibos': recibos,
        'pagos': pagos,
        'pago_pendiente': pago_pendiente,
        'puede_aprobar_pago': request.user.rol in ['admin', 'empleado'] or request.user.is_staff
    }
    
    return render(request, 'pedidos/detalle_pedido.html', context)
        
    
@login_required
def generar_remision_pdf(request, pedido_id):
    """
    Genera PDF de remisión con formato comercial completo.
    Accesible para:
    - Staff/administradores (cualquier pedido)
    - Clientes (solo sus propios pedidos con pago aprobado)
    Versión actualizada: 19/12/2024 - Incluye colores corporativos amarillos
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from datetime import datetime
    
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar permisos de acceso
    if request.user.is_staff or es_staff(request.user):
        # Staff puede ver cualquier pedido
        pass
    else:
        # Clientes solo pueden ver sus propios pedidos
        try:
            cliente = Cliente.objects.get(usuario=request.user)
            if pedido.cliente != cliente:
                messages.error(request, "No tienes permiso para acceder a este pedido.")
                return redirect('pedidos:mis_pedidos')
            
            # Verificar que el pago esté aprobado
            estados_permitidos = ['pagado', 'en_preparacion', 'listo_entrega', 'en_camino', 'entregado', 'recibido', 'programado_devolucion', 'CERRADO']
            if pedido.estado_pedido_general not in estados_permitidos:
                messages.error(request, "La remisión estará disponible una vez que tu pago sea aprobado.")
                return redirect('pedidos:detalle_mi_pedido', pedido_id=pedido_id)
                
        except Cliente.DoesNotExist:
            messages.error(request, "No tienes perfil de cliente.")
            return redirect('usuarios:inicio_cliente')
    
    # Crear el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm, 
        topMargin=2*cm, 
        bottomMargin=2*cm
    )
    
    # Colores corporativos amarillos
    AMARILLO_MULTIANDAMIOS = colors.Color(1, 0.84, 0)  # RGB: 255, 214, 0 - Color amarillo principal
    AMARILLO_OSCURO = colors.Color(0.9, 0.76, 0)       # RGB: 230, 194, 0 - Amarillo más oscuro
    GRIS_TEXTO = colors.Color(0.2, 0.2, 0.2)           # RGB: 51, 51, 51 - Gris para texto
    NEGRO = colors.black
    BLANCO = colors.white
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    titulo_empresa = ParagraphStyle(
        'TituloEmpresa',
        parent=styles['Title'],
        fontSize=20,
        textColor=GRIS_TEXTO,
        alignment=1,  # Centrado
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    titulo_documento = ParagraphStyle(
        'TituloDocumento',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=GRIS_TEXTO,
        alignment=1,  # Centrado
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=GRIS_TEXTO,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    texto_normal = ParagraphStyle(
        'TextoNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=GRIS_TEXTO,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Contenido del documento
    story = []
    
    # 1. ENCABEZADO DE LA EMPRESA
    encabezado_empresa = f"""
    <para align="center">
    <b><font size="20" color="#{int(GRIS_TEXTO.red*255):02x}{int(GRIS_TEXTO.green*255):02x}{int(GRIS_TEXTO.blue*255):02x}">MULTIANDAMIOS S.A.S</font></b><br/>
    <font size="10" color="#{int(GRIS_TEXTO.red*255):02x}{int(GRIS_TEXTO.green*255):02x}{int(GRIS_TEXTO.blue*255):02x}">
    NIT: 900.123.456-7<br/>
    Dirección: Calle 123 #45-67, Bogotá D.C.<br/>
    Teléfono: (601) 234-5678 | Email: info@multiandamios.com<br/>
    www.multiandamios.com
    </font>
    </para>
    """
    story.append(Paragraph(encabezado_empresa, texto_normal))
    story.append(Spacer(1, 20))
    
    # 2. TÍTULO DEL DOCUMENTO
    titulo_remision = """
    <para align="center">
    <b><font size="18">REMISIÓN DE EQUIPOS</font></b><br/>
    <font size="14">Número: REM-{:06d}</font>
    </para>
    """.format(pedido.id_pedido)
    story.append(Paragraph(titulo_remision, texto_normal))
    story.append(Spacer(1, 25))
    
    # 3. INFORMACIÓN DEL CLIENTE Y PEDIDO
    fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M')
    fecha_pedido = pedido.fecha.strftime('%d/%m/%Y %H:%M')
    
    # Obtener información del cliente de forma segura
    if pedido.cliente:
        cliente_info = {
            'nombre': str(pedido.cliente),
            'documento': getattr(pedido.cliente, 'documento', 'No especificado'),
            'telefono': getattr(pedido.cliente, 'telefono', 'No especificado'),
            'email': getattr(pedido.cliente, 'email', 'No especificado')
        }
    else:
        cliente_info = {
            'nombre': 'Cliente no especificado',
            'documento': 'No especificado',
            'telefono': 'No especificado',
            'email': 'No especificado'
        }
    
    # Tabla de información
    info_data = [
        ['INFORMACIÓN DEL CLIENTE', 'INFORMACIÓN DEL PEDIDO'],
        ['', ''],
        [f'Cliente: {cliente_info["nombre"]}', f'Número de Pedido: {pedido.id_pedido}'],
        [f'Documento: {cliente_info["documento"]}', f'Fecha de Pedido: {fecha_pedido}'],
        [f'Teléfono: {cliente_info["telefono"]}', f'Fecha de Remisión: {fecha_actual}'],
        [f'Email: {cliente_info["email"]}', f'Estado: {pedido.get_estado_pedido_general_display()}'],
        ['', ''],
        ['Dirección de Entrega:', ''],
        [pedido.direccion_entrega, ''],
    ]
    
    # Agregar fecha de entrega si existe
    if pedido.fecha_entrega:
        info_data.insert(-2, ['', f'Fecha de Entrega: {pedido.fecha_entrega.strftime("%d/%m/%Y %H:%M")}'])
    
    # Agregar observaciones si existen
    if pedido.notas:
        info_data.extend([
            ['Observaciones del Cliente:', ''],
            [pedido.notas, ''],
        ])
    
    # Crear tabla de información
    tabla_info = Table(info_data, colWidths=[9*cm, 9*cm])
    tabla_info.setStyle(TableStyle([
        # Encabezado con fondo amarillo
        ('BACKGROUND', (0, 0), (1, 0), AMARILLO_MULTIANDAMIOS),
        ('TEXTCOLOR', (0, 0), (1, 0), NEGRO),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('TOPPADDING', (0, 0), (1, 0), 12),
        
        # Contenido
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 2), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 2), (1, -1), 10),
        ('VALIGN', (0, 0), (1, -1), 'TOP'),
        
        # Bordes
        ('GRID', (0, 0), (1, -1), 1, NEGRO),
        ('LEFTPADDING', (0, 0), (1, -1), 8),
        ('RIGHTPADDING', (0, 0), (1, -1), 8),
        ('TOPPADDING', (0, 1), (1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (1, -1), 6),
    ]))
    
    story.append(tabla_info)
    story.append(Spacer(1, 25))
    
    # 4. DETALLE DE EQUIPOS
    story.append(Paragraph('<b>DETALLE DE EQUIPOS A ENTREGAR</b>', subtitulo))
    story.append(Spacer(1, 15))
    
    # Datos de la tabla de productos
    productos_data = [
        ['DESCRIPCIÓN', 'CANTIDAD', 'DÍAS\nRENTA', 'PRECIO\nDIARIO', 'SUBTOTAL']
    ]
    
    total_subtotal = 0
    
    # Agregar productos con validaciones ultra-robustas
    for detalle in pedido.detalles.all():
        try:
            # Verificaciones de seguridad para prevenir 'NoneType' object is not subscriptable
            if not detalle:
                print(f"[DEBUG PDF] Detalle es None, saltando...")
                continue
                
            if not hasattr(detalle, 'producto') or not detalle.producto:
                print(f"[DEBUG PDF] Detalle sin producto: {detalle}")
                continue
            
            # Obtener valores con validaciones seguras
            precio_diario = float(getattr(detalle, 'precio_diario', 0) or 0)
            cantidad = int(getattr(detalle, 'cantidad', 1) or 1)
            dias_renta = int(getattr(detalle, 'dias_renta', 1) or 1)
            
            # Calcular subtotal con manejo de errores
            try:
                subtotal = float(getattr(detalle, 'subtotal', 0) or (cantidad * dias_renta * precio_diario))
            except (TypeError, ValueError, AttributeError) as e:
                print(f"[DEBUG PDF] Error calculando subtotal: {e}")
                subtotal = cantidad * dias_renta * precio_diario
            
            total_subtotal += subtotal
            
            # Nombre del producto con validación
            nombre_producto = "Producto sin nombre"
            if detalle.producto and hasattr(detalle.producto, 'nombre') and detalle.producto.nombre:
                nombre_producto = str(detalle.producto.nombre)
            
            productos_data.append([
                nombre_producto,
                str(cantidad),
                str(dias_renta),
                f'${precio_diario:,.0f}',
                f'${subtotal:,.0f}'
            ])
            
        except Exception as e:
            print(f"[DEBUG PDF] Error procesando detalle: {e}")
            # Continuar con el siguiente detalle en caso de error
            continue
    
    # Agregar línea en blanco antes de totales
    productos_data.append(['', '', '', '', ''])
    
    # Agregar totales
    productos_data.append(['', '', '', 'SUBTOTAL:', f'${total_subtotal:,.0f}'])
    
    # IVA si aplica
    iva_valor = float(getattr(pedido, 'iva', 0) or 0)
    if iva_valor > 0:
        productos_data.append(['', '', '', 'IVA (19%):', f'${iva_valor:,.0f}'])
    
    # Transporte si aplica
    transporte_valor = float(getattr(pedido, 'costo_transporte', 0) or 0)
    if transporte_valor > 0:
        productos_data.append(['', '', '', 'TRANSPORTE:', f'${transporte_valor:,.0f}'])
    
    # Total general
    total_general = float(getattr(pedido, 'total', 0) or total_subtotal + iva_valor + transporte_valor)
    productos_data.append(['', '', '', 'TOTAL GENERAL:', f'${total_general:,.0f}'])
    
    # Crear tabla de productos
    tabla_productos = Table(productos_data, colWidths=[6*cm, 2*cm, 2*cm, 3*cm, 3*cm])
    
    # Calcular número de filas de productos (sin encabezado ni totales)
    filas_productos = len(pedido.detalles.all())
    
    tabla_productos.setStyle(TableStyle([
        # Encabezado con fondo amarillo
        ('BACKGROUND', (0, 0), (4, 0), AMARILLO_MULTIANDAMIOS),
        ('TEXTCOLOR', (0, 0), (4, 0), NEGRO),
        ('ALIGN', (0, 0), (4, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (4, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (4, 0), 11),
        ('BOTTOMPADDING', (0, 0), (4, 0), 10),
        ('TOPPADDING', (0, 0), (4, 0), 10),
        
        # Datos de productos
        ('ALIGN', (1, 1), (4, filas_productos), 'CENTER'),  # Cantidad, días, precio, subtotal centrados
        ('ALIGN', (0, 1), (0, filas_productos), 'LEFT'),    # Descripción a la izquierda
        ('FONTNAME', (0, 1), (4, filas_productos), 'Helvetica'),
        ('FONTSIZE', (0, 1), (4, filas_productos), 10),
        
        # Sección de totales con fondo amarillo más claro
        ('BACKGROUND', (3, filas_productos + 2), (4, -1), AMARILLO_OSCURO),
        ('ALIGN', (3, filas_productos + 2), (4, -1), 'RIGHT'),
        ('FONTNAME', (3, filas_productos + 2), (4, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, filas_productos + 2), (4, -1), 11),
        
        # Total general destacado
        ('BACKGROUND', (3, -1), (4, -1), AMARILLO_MULTIANDAMIOS),
        ('FONTSIZE', (3, -1), (4, -1), 12),
        
        # Bordes
        ('GRID', (0, 0), (4, filas_productos), 1, NEGRO),    # Productos
        ('GRID', (3, filas_productos + 2), (4, -1), 1, NEGRO),  # Totales
        ('VALIGN', (0, 0), (4, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (4, -1), 8),
        ('RIGHTPADDING', (0, 0), (4, -1), 8),
        ('TOPPADDING', (0, 0), (4, -1), 8),
        ('BOTTOMPADDING', (0, 0), (4, -1), 8),
    ]))
    
    story.append(tabla_productos)
    story.append(Spacer(1, 25))
    
    # 5. TÉRMINOS Y CONDICIONES
    story.append(Paragraph('<b>TÉRMINOS Y CONDICIONES</b>', subtitulo))
    
    terminos_texto = """
    <b>1. ENTREGA:</b> Los equipos se entregan en la dirección especificada en perfectas condiciones de funcionamiento. 
    El cliente debe verificar el estado de los equipos al momento de la entrega y reportar cualquier anomalía.<br/><br/>
    
    <b>2. RESPONSABILIDAD:</b> El cliente se hace responsable de los equipos desde el momento de la entrega hasta 
    su devolución. Debe mantenerlos en condiciones adecuadas de uso, almacenamiento y seguridad.<br/><br/>
    
    <b>3. DEVOLUCIÓN:</b> Los equipos deben ser devueltos en las mismas condiciones en que fueron entregados, 
    limpios, completos y en perfecto estado de funcionamiento en la fecha acordada.<br/><br/>
    
    <b>4. DAÑOS Y PÉRDIDAS:</b> Cualquier daño, deterioro, pérdida o faltante será cobrado al precio comercial 
    vigente del equipo. Se realizará una inspección detallada al momento de la devolución.<br/><br/>
    
    <b>5. MORA:</b> El retraso en la devolución generará cargos adicionales del 2% del valor de renta diaria 
    por cada día de mora, hasta un máximo del 50% del valor total del equipo.<br/><br/>
    
    <b>6. USO ADECUADO:</b> El cliente debe usar los equipos exclusivamente según las especificaciones técnicas 
    y normas de seguridad establecidas. Está prohibido el uso inadecuado, modificaciones o préstamo a terceros.
    """
    
    story.append(Paragraph(terminos_texto, texto_normal))
    story.append(Spacer(1, 30))
    
    # 6. SECCIÓN DE FIRMAS
    firmas_data = [
        ['', ''],
        ['', ''],
        ['_____________________________', '_____________________________'],
        ['ENTREGA', 'RECIBE'],
        ['Firma del Empleado MultiAndamios', 'Firma del Cliente'],
        ['', ''],
        ['Nombre: _______________________', 'Nombre: _______________________'],
        ['C.C.: _________________________', 'C.C.: _________________________'],
        ['Cargo: ________________________', 'Empresa: ______________________'],
        [f'Fecha: {fecha_actual}', 'Fecha: _______________________'],
    ]
    
    tabla_firmas = Table(firmas_data, colWidths=[9*cm, 9*cm])
    tabla_firmas.setStyle(TableStyle([
        # Líneas de firma
        ('ALIGN', (0, 2), (1, 2), 'CENTER'),
        ('BOTTOMPADDING', (0, 2), (1, 2), 15),
        
        # Títulos ENTREGA/RECIBE con fondo amarillo
        ('BACKGROUND', (0, 3), (1, 4), AMARILLO_MULTIANDAMIOS),
        ('ALIGN', (0, 3), (1, 4), 'CENTER'),
        ('FONTNAME', (0, 3), (1, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 3), (1, 4), 11),
        ('TOPPADDING', (0, 3), (1, 4), 8),
        ('BOTTOMPADDING', (0, 3), (1, 4), 8),
        
        # Campos de información
        ('ALIGN', (0, 5), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 5), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 5), (1, -1), 9),
        ('TOPPADDING', (0, 5), (1, -1), 4),
        ('BOTTOMPADDING', (0, 5), (1, -1), 4),
    ]))
    
    story.append(tabla_firmas)
    story.append(Spacer(1, 20))
    
    # 7. PIE DE PÁGINA
    pie_pagina = f"""
    <para align="center">
    <font size="8" color="gray">
    <i>Documento generado electrónicamente el {fecha_actual}<br/>
    Este documento es válido sin firma manuscrita según la Ley 527 de 1999<br/>
    Para consultas o reclamos: info@multiandamios.com | (601) 234-5678</i>
    </font>
    </para>
    """
    story.append(Paragraph(pie_pagina, texto_normal))
    
    # Construir el PDF
    doc.build(story)
    
    buffer.seek(0)
    
    # Generar timestamp único para evitar problemas de caché
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="remision_pedido_{pedido_id}_{timestamp}.pdf"'
    
    # Agregar headers para evitar caché del navegador
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

@login_required
def generar_factura_pdf(request, pedido_id):
    """
    Genera PDF de factura con formato comercial completo.
    Accesible para:
    - Staff/administradores (cualquier pedido)
    - Clientes (solo sus propios pedidos con pago aprobado)
    """
    from decimal import Decimal
    import io
    import os
    from django.conf import settings
    from django.http import FileResponse, Http404
    from django.shortcuts import redirect
    from django.contrib import messages
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from django.utils import timezone
    
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar permisos de acceso (mismo código que en remisión)
    if request.user.is_staff or es_staff(request.user):
        # Staff puede ver cualquier pedido
        pass
    else:
        # Clientes solo pueden ver sus propios pedidos
        try:
            cliente = Cliente.objects.get(usuario=request.user)
            if pedido.cliente != cliente:
                messages.error(request, "No tienes permiso para acceder a este pedido.")
                return redirect('pedidos:mis_pedidos')
            
            # Verificar que el pago esté aprobado
            estados_permitidos = ['pagado', 'en_preparacion', 'listo_entrega', 'en_camino', 'entregado', 'recibido', 'programado_devolucion', 'CERRADO']
            if pedido.estado_pedido_general not in estados_permitidos:
                messages.error(request, "La factura estará disponible una vez que tu pago sea aprobado.")
                return redirect('pedidos:detalle_mi_pedido', pedido_id=pedido_id)
                
        except Cliente.DoesNotExist:
            messages.error(request, "No tienes perfil de cliente.")
            return redirect('usuarios:inicio_cliente')

    def format_currency(amount):
        """Formatea valores monetarios con separadores de miles y dos decimales"""
        return f"${amount:,.0f}"

    try:
        # Obtener y validar el pedido
        pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
        
        # Verificar que el usuario tenga acceso a este pedido
        if request.user != pedido.cliente.usuario and not request.user.is_staff:
            messages.error(request, "No tienes permiso para ver esta factura.")
            return redirect('pedidos:lista_pedidos')

        # Verificar que el pedido tenga detalles
        if not pedido.detalles.exists():
            messages.error(request, "El pedido no tiene productos para generar una factura.")
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)

        # Crear el PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Definir medidas y estilos consistentes
        margin_left = 50
        margin_right = 50
        content_width = width - margin_left - margin_right
        
        # Colores corporativos
        amarillo = colors.HexColor('#FFD600')
        negro = colors.black
        gris_texto = colors.HexColor('#666666')

        def draw_header():
            """Dibuja el encabezado de la factura"""            # Fondo y borde del header
            p.setFillColor(amarillo)
            p.rect(0, height - 120, width, 120, fill=True)
            # Línea separadora inferior del header
            p.setStrokeColor(colors.HexColor('#E0E0E0'))
            p.setLineWidth(2)
            p.line(0, height - 120, width, height - 120)
            
            # Logo
            logo_path = os.path.join(settings.MEDIA_ROOT, 'productos', 'Logo-Teinco-Color.webp')
            if os.path.exists(logo_path):
                p.drawImage(logo_path, margin_left, height - 110, width=90, height=80, preserveAspectRatio=True)
            
            # Datos de la empresa
            company_x = margin_left + 120
            
            # Nombre de la empresa
            p.setFillColor(negro)
            p.setFont("Helvetica-Bold", 20)
            p.drawString(company_x, height - 55, "MULTIANDAMIOS S.A.S.")
            
            # Información de contacto
            p.setFont("Helvetica", 9)
            p.drawString(company_x, height - 70, "NIT: 900.252.510-1")
            p.drawString(company_x, height - 85, "Cra. 128 #22A-45, Bogotá, Colombia")
            p.drawString(company_x, height - 100, "Tel: +57 310 574 2020 | Email: info@multiandamios.co")
            
            # Número de factura y fecha
            factura_x = width - margin_right - 200
              # Recuadro número de factura con fondo y sombra
            # Sombra
            p.setFillColor(colors.HexColor('#E0E0E0'))
            p.rect(factura_x + 2, height - 52, 190, 25, fill=True)
            
            # Fondo
            p.setFillColor(amarillo)
            p.rect(factura_x, height - 50, 190, 25, fill=True)
            
            # Borde
            p.setStrokeColor(colors.HexColor('#CCCCCC'))
            p.setLineWidth(1)
            p.rect(factura_x, height - 50, 190, 25, stroke=True)
            
            # Número de factura
            p.setFillColor(negro)
            p.setFont("Helvetica-Bold", 12)
            num_text = f"FACTURA No. {pedido.id_pedido:06d}"
            p.drawString(factura_x + 10, height - 35, num_text)
            
            # Fecha de emisión
            p.setFont("Helvetica", 9)
            fecha_str = f"Fecha de emisión: {pedido.fecha.strftime('%d/%m/%Y %H:%M')}"
            p.drawString(factura_x + 10, height - 70, fecha_str)

        def draw_client_info():
            """Dibuja la sección de información del cliente"""            # Ajustar espaciado para mejor distribución
            client_box_y = height - 140  # Más cerca del header
            client_box_height = 90  # Un poco más compacto
              # Recuadro para datos del cliente con sombra
            # Efecto de sombra
            p.setFillColor(colors.HexColor('#E0E0E0'))
            p.rect(margin_left + 2, client_box_y - client_box_height - 2, 
                   content_width, client_box_height, fill=True)
            
            # Recuadro principal
            p.setFillColor(colors.white)
            p.rect(margin_left, client_box_y - client_box_height, 
                   content_width, client_box_height, fill=True)
            
            # Borde del recuadro
            p.setStrokeColor(colors.HexColor('#CCCCCC'))
            p.setLineWidth(1)
            p.rect(margin_left, client_box_y - client_box_height, 
                   content_width, client_box_height, stroke=True)
            
            # Título "DATOS DEL CLIENTE"
            p.setFillColor(amarillo)
            p.rect(margin_left, client_box_y - 25, 130, 25, fill=True)
            p.setFillColor(negro)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(margin_left + 10, client_box_y - 18, "DATOS DEL CLIENTE")
            
            # Datos del cliente
            datos_cliente = [
                ("Cliente:", f"{pedido.cliente}"),
                ("Identificación:", f"{getattr(pedido.cliente.usuario, 'numero_identidad', 'N/A')}"),
                ("Dirección:", f"{pedido.direccion_entrega}"),
                ("Email:", f"{pedido.cliente.usuario.email}"),
                ("Teléfono:", f"{getattr(pedido.cliente.usuario, 'telefono', 'N/A')}")
            ]
            
            for i, (label, valor) in enumerate(datos_cliente):
                y_pos = client_box_y - 50 - (i * 15)
                p.setFillColor(gris_texto)
                p.setFont("Helvetica-Bold", 9)
                p.drawString(margin_left + 15, y_pos, label)
                p.setFillColor(negro)
                p.setFont("Helvetica", 9)
                p.drawString(margin_left + 100, y_pos, valor)

        def draw_products_table():
            """Dibuja la tabla de productos"""
            # Definir columnas y calcular posiciones X primero
            cols = [
                ('Producto', content_width * 0.45),
                ('Cant.', content_width * 0.10),
                ('Días', content_width * 0.10),
                ('Precio Unit.', content_width * 0.15),
                ('Subtotal', content_width * 0.20)
            ]
            
            # Calcular posiciones X para las columnas
            x_positions = []
            current_x = margin_left
            for _, ancho in cols:
                x_positions.append(current_x)
                current_x += ancho

            # Posición y dimensiones de la tabla
            table_y = height - 310  # Bajamos 30 unidades
            num_productos = pedido.detalles.count()
            altura_minima = 100  # Altura mínima para al menos 3 productos
            altura_por_producto = 25  # Altura por cada producto
            altura_tabla = max(altura_minima, (num_productos + 1) * altura_por_producto)  # +1 para el encabezado
            
            # Efecto de sombra
            p.setFillColor(colors.HexColor('#E0E0E0'))
            p.rect(margin_left + 2, table_y - altura_tabla - 2, content_width, altura_tabla, fill=True)
            
            # Marco principal
            p.setFillColor(colors.white)
            p.rect(margin_left, table_y - altura_tabla, content_width, altura_tabla, fill=True)
            p.setStrokeColor(colors.HexColor('#CCCCCC'))
            p.setLineWidth(1)
            p.rect(margin_left, table_y - altura_tabla, content_width, altura_tabla, stroke=True)
            
            # Líneas verticales separadoras para las columnas
            for x_pos in x_positions[1:]:  # Para cada columna excepto la primera
                p.line(x_pos, table_y, x_pos, table_y - altura_tabla)
              # Las columnas y posiciones X ya están definidas arriba
            
            # Encabezados
            p.setFillColor(amarillo)
            p.rect(margin_left, table_y, content_width, 20, fill=True)
            
            # Títulos de columnas
            p.setFillColor(negro)
            p.setFont("Helvetica-Bold", 10)
            for i, (titulo, ancho) in enumerate(cols):
                text_width = p.stringWidth(titulo, "Helvetica-Bold", 10)
                x_centro = x_positions[i] + (ancho / 2)
                p.drawString(x_centro - text_width/2, table_y + 6, titulo)
            
            # Contenido
            y = table_y - 25
            total = Decimal('0')
            p.setFont("Helvetica", 10)
            
            for i, detalle in enumerate(pedido.detalles.all()):
                try:
                    # Verificaciones de seguridad para prevenir 'NoneType' object is not subscriptable
                    if not detalle:
                        print(f"[DEBUG PDF FACTURA] Detalle es None, saltando...")
                        continue
                        
                    if not hasattr(detalle, 'producto') or not detalle.producto:
                        print(f"[DEBUG PDF FACTURA] Detalle sin producto: {detalle}")
                        continue
                    
                    # Fondo alternado
                    if i % 2 == 0:
                        p.setFillColor(colors.HexColor('#F8F8F8'))
                        p.rect(margin_left + 1, y - 15, content_width - 2, 20, fill=True)
                    
                    p.setFillColor(negro)
                    
                    # Producto con validación
                    nombre = "Producto sin nombre"
                    if detalle.producto and hasattr(detalle.producto, 'nombre') and detalle.producto.nombre:
                        nombre = str(detalle.producto.nombre)
                    
                    nombre_cortado = (nombre[:45] + '...') if len(nombre) > 45 else nombre
                    p.drawString(x_positions[0] + 5, y, nombre_cortado)
                    
                    # Cantidad (centrado) con validación
                    cantidad = getattr(detalle, 'cantidad', 1) or 1
                    cant_str = str(cantidad)
                    cant_width = p.stringWidth(cant_str, "Helvetica", 10)
                    x_cant = x_positions[1] + (cols[1][1] / 2) - (cant_width / 2)
                    p.drawString(x_cant, y, cant_str)
                    
                    # Días (centrado) con validación
                    dias_renta = getattr(detalle, 'dias_renta', 1) or 1
                    dias_str = str(dias_renta)
                    dias_width = p.stringWidth(dias_str, "Helvetica", 10)
                    x_meses = x_positions[2] + (cols[2][1] / 2) - (dias_width / 2)
                    p.drawString(x_meses, y, dias_str)
                    
                    # Precio unitario (derecha) con validación
                    precio_diario = getattr(detalle, 'precio_diario', 0) or 0
                    precio_str = format_currency(precio_diario)
                    p.drawRightString(x_positions[3] + cols[3][1] - 5, y, precio_str)
                    
                    # Subtotal (derecha) con validación
                    subtotal = getattr(detalle, 'subtotal', 0) or 0
                    subtotal_str = format_currency(subtotal)
                    p.drawRightString(x_positions[4] + cols[4][1] - 5, y, subtotal_str)
                    
                except Exception as e:
                    print(f"[DEBUG PDF FACTURA] Error procesando detalle: {e}")
                    # Continuar con el siguiente detalle en caso de error
                    continue
                
                y -= 20
                total += detalle.subtotal

            return total, y, x_positions, cols

        def draw_totals(total, y, x_positions, cols):
            """Dibuja la sección de totales"""
            # Cálculos
            iva = total * Decimal('0.19')
            total_con_iva = total + iva
            
            # Área de totales - ajustada más a la izquierda y más ancha
            totals_x = x_positions[-2] - 100  # Mover más a la izquierda
            totals_width = (cols[-2][1] + cols[-1][1]) + 100  # Hacer más ancha
            
            # Marco para totales con sombra
            # Efecto de sombra
            p.setFillColor(colors.HexColor('#E0E0E0'))
            p.rect(totals_x + 2, y - 52, totals_width, 70, fill=True)
            
            # Marco principal
            p.setFillColor(colors.HexColor('#F8F8F8'))
            p.rect(totals_x, y - 50, totals_width, 70, fill=True)
            p.setStrokeColor(colors.HexColor('#CCCCCC'))
            p.setLineWidth(1)
            p.rect(totals_x, y - 50, totals_width, 70, stroke=True)
            
            # Subtotal
            p.setFillColor(gris_texto)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(totals_x + 10, y - 15, "SUBTOTAL:")
            p.setFillColor(negro)
            p.drawRightString(totals_x + totals_width - 10, y - 15, f"${total:,.0f}")
            
            # IVA
            p.setFillColor(gris_texto)
            p.drawString(totals_x + 10, y - 35, "IVA (19%):")
            p.setFillColor(negro)
            p.drawRightString(totals_x + totals_width - 10, y - 35, f"${iva:,.0f}")
            
            # Total
            p.setFillColor(amarillo)
            p.rect(totals_x, y - 50, totals_width, 20, fill=True)
            p.setFillColor(negro)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(totals_x + 10, y - 45, "TOTAL A PAGAR:")
            p.drawRightString(totals_x + totals_width - 10, y - 45, f"${total_con_iva:,.0f}")
            
            return y - 70

        def draw_footer(y_final):
            """Dibuja el pie de página"""
            # Ajustar posición más arriba
            y_final = y_final + 100  # Mover más arriba
            
            # Recuadro principal con información de pago y condiciones
            # Efecto de sombra
            p.setFillColor(colors.HexColor('#E0E0E0'))
            p.rect(margin_left + 2, y_final - 82, content_width, 75, fill=True)
            
            # Marco principal
            p.setFillColor(colors.HexColor('#F8F8F8'))
            p.rect(margin_left, y_final - 80, content_width, 75, fill=True)
            p.setStrokeColor(colors.HexColor('#CCCCCC'))
            p.setLineWidth(1)
            p.rect(margin_left, y_final - 80, content_width, 75, stroke=True)
            
            # Título de la sección
            p.setFillColor(amarillo)
            p.rect(margin_left, y_final - 30, 130, 25, fill=True)
            p.setFillColor(negro)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(margin_left + 10, y_final - 23, "INFORMACIÓN DE PAGO")
            
            # Información de pago y condiciones
            p.setFillColor(gris_texto)
            p.setFont("Helvetica-Bold", 9)
            
            # Columna izquierda
            p.drawString(margin_left + 15, y_final - 50, "Método de pago:")
            p.drawString(margin_left + 15, y_final - 65, "Condiciones:")
            
            p.setFillColor(negro)
            p.setFont("Helvetica", 9)
            metodo = pedido.metodo_pago if pedido.metodo_pago else "No especificado"
            p.drawString(margin_left + 100, y_final - 50, metodo)
            p.drawString(margin_left + 100, y_final - 65, "Pago contra entrega / Términos y condiciones aplican")
            
            # Columna derecha
            if pedido.ref_pago:
                p.setFillColor(gris_texto)
                p.setFont("Helvetica-Bold", 9)
                p.drawString(margin_left + content_width/2 + 15, y_final - 50, "Referencia de pago:")
                p.setFillColor(negro)
                p.setFont("Helvetica", 9)
                p.drawString(margin_left + content_width/2 + 120, y_final - 50, pedido.ref_pago)

            # Notas del pedido si existen
            if pedido.notas:
                p.setFillColor(gris_texto)
                p.setFont("Helvetica-Bold", 9)
                p.drawString(margin_left + content_width/2 + 15, y_final - 65, "Notas:")
                p.setFillColor(negro)
                p.setFont("Helvetica", 9)
                notas = pedido.notas if len(pedido.notas) <= 50 else pedido.notas[:47] + "..."
                p.drawString(margin_left + content_width/2 + 120, y_final - 65, notas)

        def draw_legal_footer():
            """Dibuja el pie de página legal"""
            p.setFillColor(gris_texto)
            p.setFont("Helvetica", 8)
            
            # Información legal
            legal_text = "Esta factura es un documento válido para efectos fiscales. | MULTIANDAMIOS S.A.S."
            p.drawString(margin_left, 40, legal_text)
            
            # Resolución DIAN (ejemplo)
            resolucion_text = "Resolución DIAN No. XXXXX del XX/XX/XXXX"
            p.drawString(margin_left, 30, resolucion_text)
            
            # Régimen tributario
            regimen_text = "Régimen: RESPONSABLE DE IVA"
            p.drawString(margin_left, 20, regimen_text)

        try:
            # Generar la factura
            draw_header()
            draw_client_info()
            total, y_pos, x_positions, cols = draw_products_table()
            draw_totals(total, y_pos, x_positions, cols)
            draw_footer(y_pos - 120)  # Ajustar posición del footer
            draw_legal_footer()  # Agregar pie de página legal
            
            # Finalizar el PDF
            p.showPage()
            p.save()
            buffer.seek(0)
            
            # Retornar el archivo PDF
            response = FileResponse(buffer, as_attachment=True, 
                                 filename=f'factura_{pedido.id_pedido}.pdf',
                                 content_type='application/pdf')
            return response

        except Exception as e:
            # Error en la generación del PDF
            messages.error(request, f"Error al generar la factura: {str(e)}")
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)

    except Exception as e:
        # Error al obtener el pedido o validar permisos
        messages.error(request, f"Error al procesar la solicitud: {str(e)}")
        return redirect('pedidos:lista_pedidos')

@login_required
@login_required
@user_passes_test(es_cliente, login_url='/panel/')
def mis_pedidos(request):
    """Vista para que los clientes vean sus pedidos"""
    # Esta vista es solo para clientes, los admins/empleados son redirigidos por el decorador
    # Obtener el cliente asociado al usuario
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, "No tienes perfil de cliente.")
        return redirect('usuarios:inicio_cliente')
    
    # Obtener los pedidos del cliente
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    
    # Procesar pedidos pendientes de pago
    for pedido in pedidos:
        if pedido.estado_pedido_general == 'pendiente_pago':
            # Verificar si el pago está vencido
            if pedido.esta_vencido_pago():
                pedido.estado_pedido_general = 'pago_vencido'
                pedido.save()
            elif pedido.fecha_limite_pago:
                # Calcular tiempo restante para pedidos pendientes
                tiempo_restante = pedido.get_tiempo_restante_pago()
                if tiempo_restante:
                    horas = int(tiempo_restante.total_seconds() / 3600)
                    minutos = int((tiempo_restante.total_seconds() % 3600) / 60)
                    pedido.tiempo_restante_str = f"{horas}h {minutos}m"
    
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(es_cliente, login_url='/panel/')
def detalle_mi_pedido(request, pedido_id):
    """Vista para que un cliente vea el detalle de uno de sus pedidos"""
    # Esta vista es solo para clientes, los admins/empleados son redirigidos por el decorador
    # Obtener el cliente asociado al usuario
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, "No tienes perfil de cliente.")
        return redirect('usuarios:inicio_cliente')
    
    # Obtener el pedido asegurando que pertenezca al cliente actual
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente=cliente)
    
    # Verificar si hay tiempo límite de pago y calcular tiempo restante
    if pedido.estado_pedido_general == 'pendiente_pago' and pedido.fecha_limite_pago:
        tiempo_restante = pedido.get_tiempo_restante_pago()
        if tiempo_restante:
            horas = int(tiempo_restante.total_seconds() / 3600)
            minutos = int((tiempo_restante.total_seconds() % 3600) / 60)
            pedido.tiempo_restante_str = f"{horas}h {minutos}m"
    
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all().select_related('producto'),
        'cliente': cliente,
    }
    
    return render(request, 'pedidos/detalle_mi_pedido.html', context)

@login_required
def programar_devolucion(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente__usuario=request.user)
    
    if request.method == 'POST':
        fecha_devolucion = request.POST.get('fecha_devolucion')
        try:
            # Convertir la fecha del formulario a datetime
            fecha_devolucion = timezone.datetime.strptime(fecha_devolucion, '%Y-%m-%d').date()
            fecha_devolucion = timezone.make_aware(timezone.datetime.combine(fecha_devolucion, timezone.datetime.min.time()))
            
            # Validar que la fecha no sea anterior a hoy
            if fecha_devolucion < timezone.now():
                messages.error(request, 'La fecha de devolución no puede ser anterior a hoy.')
                return redirect('pedidos:programar_devolucion', pedido_id=pedido_id)
            
            # Guardar la fecha programada
            pedido.fecha_devolucion_programada = fecha_devolucion
            pedido.estado_pedido_general = 'programado_devolucion'
            pedido.save()
            
            messages.success(request, 'La devolución ha sido programada exitosamente.')
            return redirect('pedidos:detalle_mi_pedido', pedido_id=pedido_id)
            
        except ValueError:
            messages.error(request, 'Formato de fecha inválido. Por favor, use el selector de fecha.')
            return redirect('pedidos:programar_devolucion', pedido_id=pedido_id)
    
    return render(request, 'pedidos/programar_devolucion.html', {
        'pedido': pedido,
        'fecha_minima': timezone.now().date().isoformat(),
        'fecha_sugerida': (pedido.fecha_vencimiento or timezone.now()).date().isoformat()
    })

@login_required
@user_passes_test(es_staff)
def agregar_cliente(request):
    """Vista para agregar un nuevo cliente desde el panel de administración"""
    if request.method == 'POST':
        form = ClienteCompletoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verificar si ya existe un usuario con ese username
                    if Usuario.objects.filter(username=form.cleaned_data['username']).exists():
                        form.add_error('username', 'Ya existe un usuario con este nombre de usuario.')
                        return render(request, 'pedidos/agregar_cliente.html', {'form': form})
                    
                    # Verificar email si se proporciona
                    email = form.cleaned_data.get('email')
                    if email and Usuario.objects.filter(email=email).exists():
                        form.add_error('email', 'Ya existe un usuario con este correo electrónico.')
                        return render(request, 'pedidos/agregar_cliente.html', {'form': form})
                    
                    # Verificar número de identidad si se proporciona
                    numero_identidad = form.cleaned_data.get('numero_identidad')
                    if numero_identidad and Usuario.objects.filter(numero_identidad=numero_identidad).exists():
                        form.add_error('numero_identidad', 'Ya existe un usuario con este número de identidad.')
                        return render(request, 'pedidos/agregar_cliente.html', {'form': form})
                    
                    # Crear el usuario con rol 'cliente'
                    usuario = Usuario.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password']
                    )
                    usuario.first_name = form.cleaned_data.get('first_name', '')
                    usuario.last_name = form.cleaned_data.get('last_name', '')
                    usuario.email = form.cleaned_data.get('email', '')
                    usuario.rol = 'cliente'
                    usuario.numero_identidad = form.cleaned_data.get('numero_identidad', '')
                    usuario.save()
                    
                    # Crear o obtener el cliente asociado al usuario
                    # Usamos get_or_create para evitar duplicados
                    cliente, created = Cliente.objects.get_or_create(
                        usuario=usuario,
                        defaults={
                            'telefono': form.cleaned_data.get('telefono', ''),
                            'direccion': form.cleaned_data.get('direccion', '')
                        }
                    )
                    
                    # Si no fue creado, actualizar los datos
                    if not created:
                        cliente.telefono = form.cleaned_data.get('telefono', '')
                        cliente.direccion = form.cleaned_data.get('direccion', '')
                        cliente.save()
                    
                    messages.success(request, f'Cliente {usuario.first_name} {usuario.last_name} ({usuario.username}) creado exitosamente.')
                    return redirect('pedidos:lista_clientes')
                    
            except IntegrityError as e:
                error_message = str(e)
                if 'usuarios_cliente.usuario_id' in error_message or 'UNIQUE constraint failed' in error_message:
                    # Mensaje más específico para el error de cliente duplicado
                    messages.error(request, 'Error: Este usuario ya tiene un cliente asociado. Intente crear otro cliente con un nombre de usuario diferente.')
                elif 'usuarios_usuario.username' in error_message:
                    messages.error(request, f'Error: El nombre de usuario "{form.cleaned_data.get("username", "")}" ya está en uso.')
                elif 'usuarios_usuario.email' in error_message:
                    messages.error(request, f'Error: El correo electrónico "{form.cleaned_data.get("email", "")}" ya está registrado.')
                elif 'usuarios_usuario.numero_identidad' in error_message:
                    messages.error(request, f'Error: El número de identidad "{form.cleaned_data.get("numero_identidad", "")}" ya está registrado.')
                else:
                    messages.error(request, f'Error de integridad de datos: {error_message}')
                    
            except Exception as e:
                messages.error(request, f'Error inesperado al crear el cliente: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = ClienteCompletoForm()
        
    return render(request, 'pedidos/agregar_cliente.html', {'form': form})

@login_required
@user_passes_test(es_staff)
def cambiar_estado_cliente(request, usuario_id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        messages.success(request, f'El estado del cliente {usuario.username} ha sido actualizado.')
    return redirect('pedidos:lista_clientes')

@login_required
@user_passes_test(es_staff)
def cambiar_estado_producto(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id_producto=producto_id)
        producto.activo = not producto.activo
        producto.save()
        messages.success(request, f'El estado del producto {producto.nombre} ha sido actualizado.')
    return redirect('pedidos:admin_productos')
        
    return render(request, 'pedidos/agregar_cliente.html', {'form': form})

@login_required
@user_passes_test(es_staff)
def cambiar_estado_cliente(request, usuario_id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        messages.success(request, f'El estado del cliente {usuario.username} ha sido actualizado.')
    return redirect('pedidos:lista_clientes')

@login_required
@user_passes_test(es_staff)
def cambiar_estado_producto(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id_producto=producto_id)
        producto.activo = not producto.activo
        producto.save()
        messages.success(request, f'El estado del producto {producto.nombre} ha sido actualizado.')
    return redirect('pedidos:admin_productos')

@login_required
@user_passes_test(lambda u: u.rol in ['admin', 'empleado'] or u.is_staff)
def aprobar_pago(request, pedido_id):
    """Vista para que empleados/admin aprueben o rechacen pagos"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')  # 'aprobar' o 'rechazar'
        notas_admin = request.POST.get('notas_admin', '')
        
        if not accion:
            messages.error(request, 'Debe seleccionar una acción.')
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
        
        try:
            with transaction.atomic():
                # Buscar el pago pendiente asociado al pedido
                from usuarios.models import MetodoPago
                pago = MetodoPago.objects.filter(
                    pedido=pedido, 
                    estado='pendiente'
                ).first()
                
                if not pago:
                    messages.error(request, 'No se encontró un pago pendiente para este pedido.')
                    return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
                
                if accion == 'aprobar':
                    # Aprobar el pago
                    pago.estado = 'aprobado'
                    pago.fecha_verificacion = timezone.now()
                    pago.verificado_por = request.user
                    pago.notas = f"{pago.notas}\n\nAprobado por {request.user.username}: {notas_admin}".strip()
                    pago.save()
                    
                    # Actualizar estado del pedido directamente
                    pedido.estado_pedido_general = 'pagado'
                    pedido.fecha_pago = timezone.now()
                    pedido.metodo_pago = pago.tipo
                    pedido.save()
                    
                    # Confirmar la reserva de productos en los detalles
                    for detalle in pedido.detalles.all():
                        producto = detalle.producto
                        # Mover de cantidad_disponible a cantidad_en_renta
                        if producto.cantidad_disponible >= detalle.cantidad:
                            producto.cantidad_disponible -= detalle.cantidad
                            producto.cantidad_en_renta += detalle.cantidad
                            producto.save()
                    
                    messages.success(request, f'Pago aprobado exitosamente. Pedido #{pedido.id_pedido} ahora está pagado.')
                    
                elif accion == 'rechazar':
                    # Rechazar el pago
                    pago.estado = 'rechazado'
                    pago.fecha_verificacion = timezone.now()
                    pago.verificado_por = request.user
                    pago.notas = f"{pago.notas}\n\nRechazado por {request.user.username}: {notas_admin}".strip()
                    pago.save()
                    
                    # Actualizar estado del pedido manualmente (no hay auto-procesamiento para rechazo)
                    pedido.estado_pedido_general = 'pago_rechazado'
                    pedido.save()
                    
                    # Liberar inventario (devolver productos al disponible)
                    for detalle in pedido.detalles.all():
                        producto = detalle.producto
                        producto.cantidad_disponible += detalle.cantidad
                        producto.save()
                    
                    messages.warning(request, f'Pago rechazado. Pedido #{pedido.id_pedido} marcado como pago rechazado.')
                
                return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
                
        except Exception as e:
            messages.error(request, f'Error al procesar la acción: {str(e)}')
            return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)
    
    return redirect('pedidos:detalle_pedido', pedido_id=pedido_id)

# =====================================
# VISTAS PARA REPORTES DE TIEMPO
# =====================================

@login_required
def mis_pedidos_tiempo(request):
    """Vista para que los clientes vean el tiempo restante de sus pedidos"""
    if not es_cliente(request.user):
        messages.error(request, 'Acceso denegado. Solo clientes pueden ver esta información.')
        return redirect('pedidos:lista_pedidos')
    
    try:
        cliente = request.user.cliente
    except:
        messages.error(request, 'No se encontró información de cliente para este usuario.')
        return redirect('pedidos:lista_pedidos')
    
    # Obtener pedidos activos (con renta en curso)
    pedidos_activos = Pedido.objects.filter(
        cliente=cliente,
        estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
    ).order_by('-fecha')
    
    # Separar por estado de tiempo
    pedidos_normales = []
    pedidos_pronto_vencer = []
    pedidos_vencidos = []
    pedidos_sin_iniciar = []
    
    for pedido in pedidos_activos:
        estado_tiempo = pedido.get_estado_tiempo_renta()
        if estado_tiempo == 'vencido':
            pedidos_vencidos.append(pedido)
        elif estado_tiempo in ['vence_hoy', 'vence_pronto']:
            pedidos_pronto_vencer.append(pedido)
        elif estado_tiempo == 'normal':
            pedidos_normales.append(pedido)
        else:
            pedidos_sin_iniciar.append(pedido)
    
    context = {
        'pedidos_normales': pedidos_normales,
        'pedidos_pronto_vencer': pedidos_pronto_vencer,
        'pedidos_vencidos': pedidos_vencidos,
        'pedidos_sin_iniciar': pedidos_sin_iniciar,
        'total_activos': len(pedidos_activos),
    }
    
    return render(request, 'pedidos/mis_pedidos_tiempo.html', context)

@login_required
@user_passes_test(es_staff)
def reporte_tiempo_global(request):
    """Vista para admin/empleados con reporte global de tiempo de todos los pedidos"""
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    cliente_filtro = request.GET.get('cliente', '')
    tiempo_filtro = request.GET.get('tiempo', '')  # normal, vence_pronto, vencido
    
    # Obtener pedidos con renta activa
    pedidos = Pedido.objects.filter(
        estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
    ).select_related('cliente__usuario').order_by('-fecha')
    
    # Aplicar filtros
    if estado_filtro:
        pedidos = pedidos.filter(estado_pedido_general=estado_filtro)
    
    if cliente_filtro:
        pedidos = pedidos.filter(
            Q(cliente__usuario__first_name__icontains=cliente_filtro) |
            Q(cliente__usuario__last_name__icontains=cliente_filtro) |
            Q(cliente__usuario__numero_identidad__icontains=cliente_filtro)
        )
    
    # Separar por estado de tiempo y aplicar filtro de tiempo
    pedidos_por_estado = {
        'normal': [],
        'vence_pronto': [],
        'vence_hoy': [],
        'vencido': [],
        'sin_iniciar': []
    }
    
    for pedido in pedidos:
        estado_tiempo = pedido.get_estado_tiempo_renta()
        if estado_tiempo == 'vencido':
            pedidos_por_estado['vencido'].append(pedido)
        elif estado_tiempo == 'vence_hoy':
            pedidos_por_estado['vence_hoy'].append(pedido)
        elif estado_tiempo == 'vence_pronto':
            pedidos_por_estado['vence_pronto'].append(pedido)
        elif estado_tiempo == 'normal':
            pedidos_por_estado['normal'].append(pedido)
        else:
            pedidos_por_estado['sin_iniciar'].append(pedido)
    
    # Filtrar por estado de tiempo si se especifica
    if tiempo_filtro:
        if tiempo_filtro == 'criticos':
            # Mostrar solo vencidos y que vencen hoy
            pedidos_filtrados = pedidos_por_estado['vencido'] + pedidos_por_estado['vence_hoy']
        elif tiempo_filtro == 'alerta':
            # Mostrar próximos a vencer
            pedidos_filtrados = pedidos_por_estado['vence_pronto']
        elif tiempo_filtro in pedidos_por_estado:
            pedidos_filtrados = pedidos_por_estado[tiempo_filtro]
        else:
            pedidos_filtrados = list(pedidos)
    else:
        pedidos_filtrados = list(pedidos)
    
    # Estadísticas
    estadisticas = {
        'total_activos': len(pedidos),
        'total_vencidos': len(pedidos_por_estado['vencido']),
        'total_vence_hoy': len(pedidos_por_estado['vence_hoy']),
        'total_vence_pronto': len(pedidos_por_estado['vence_pronto']),
        'total_normales': len(pedidos_por_estado['normal']),
        'total_sin_iniciar': len(pedidos_por_estado['sin_iniciar']),
        'porcentaje_criticos': round((len(pedidos_por_estado['vencido']) + len(pedidos_por_estado['vence_hoy'])) / max(len(pedidos), 1) * 100, 1),
    }
    
    context = {
        'pedidos': pedidos_filtrados,
        'pedidos_por_estado': pedidos_por_estado,
        'estadisticas': estadisticas,
        'filtros': {
            'estado': estado_filtro,
            'cliente': cliente_filtro,
            'tiempo': tiempo_filtro,
        },
        'estados_pedido': Pedido.ESTADO_CHOICES,
    }
    
    return render(request, 'pedidos/reporte_tiempo_global.html', context)

@login_required
def detalle_tiempo_pedido(request, pedido_id):
    """Vista detallada del tiempo de un pedido específico"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    # Verificar permisos
    if es_cliente(request.user):
        if not hasattr(request.user, 'cliente') or pedido.cliente != request.user.cliente:
            messages.error(request, 'No tienes permiso para ver este pedido.')
            return redirect('pedidos:mis_pedidos_tiempo')
    elif not es_staff(request.user):
        messages.error(request, 'Acceso denegado.')
        return redirect('pedidos:lista_pedidos')
    
    # Información del pedido
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all().order_by('producto__nombre'),
        'tiempo_info': {
            'fecha_inicio': pedido.get_fecha_inicio_renta(),
            'fecha_fin': pedido.get_fecha_fin_renta(),
            'tiempo_restante': pedido.get_tiempo_restante_renta(),
            'tiempo_humanizado': pedido.get_tiempo_restante_renta_humanizado(),
            'estado_tiempo': pedido.get_estado_tiempo_renta(),
            'porcentaje_transcurrido': pedido.get_porcentaje_tiempo_transcurrido(),
            'debe_notificar': pedido.debe_notificar_vencimiento(),
        }
    }
    
    return render(request, 'pedidos/detalle_tiempo_pedido.html', context)

@login_required
@user_passes_test(es_staff)
def notificaciones_vencimiento(request):
    """Vista para gestionar notificaciones de vencimiento"""
    
    # Pedidos que necesitan notificación
    pedidos_criticos = []
    pedidos_alerta = []
    
    pedidos_activos = Pedido.objects.filter(
        estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
    ).select_related('cliente__usuario')
    
    for pedido in pedidos_activos:
        estado_tiempo = pedido.get_estado_tiempo_renta()
        if estado_tiempo in ['vencido', 'vence_hoy']:
            pedidos_criticos.append(pedido)
        elif estado_tiempo == 'vence_pronto':
            pedidos_alerta.append(pedido)
    
    # Procesar acciones
    if request.method == 'POST':
        accion = request.POST.get('accion')
        pedido_id = request.POST.get('pedido_id')
        
        if accion and pedido_id:
            try:
                pedido = Pedido.objects.get(id_pedido=pedido_id)
                
                if accion == 'marcar_notificado':
                    # En un sistema real, aquí marcarías que ya se notificó al cliente
                    messages.success(request, f'Pedido #{pedido_id} marcado como notificado.')
                
                elif accion == 'extender_renta':
                    # Aquí podrías implementar lógica para extender la renta
                    dias_extension = int(request.POST.get('dias_extension', 7))
                    # Lógica para extender...
                    messages.success(request, f'Renta del pedido #{pedido_id} extendida por {dias_extension} días.')
                
                elif accion == 'contactar_cliente':
                    # Aquí podrías enviar email/SMS al cliente
                    messages.info(request, f'Cliente del pedido #{pedido_id} contactado.')
                
            except Pedido.DoesNotExist:
                messages.error(request, 'Pedido no encontrado.')
    
    context = {
        'pedidos_criticos': pedidos_criticos,
        'pedidos_alerta': pedidos_alerta,
        'total_criticos': len(pedidos_criticos),
        'total_alerta': len(pedidos_alerta),
    }
    
    return render(request, 'pedidos/notificaciones_vencimiento.html', context)

@login_required
@user_passes_test(es_staff)
def dashboard_tiempo(request):
    """Dashboard principal para el manejo de tiempo de rentas"""
    
    # Estadísticas generales
    pedidos_activos = Pedido.objects.filter(
        estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
    )
    
    total_activos = pedidos_activos.count()
    
    # Contar por estado de tiempo
    contadores = {
        'vencidos': 0,
        'vence_hoy': 0,
        'vence_pronto': 0,
        'normales': 0,
        'sin_iniciar': 0,
    }
    
    pedidos_urgentes = []
    
    for pedido in pedidos_activos:
        estado_tiempo = pedido.get_estado_tiempo_renta()
        if estado_tiempo == 'vencido':
            contadores['vencidos'] += 1
            pedidos_urgentes.append(pedido)
        elif estado_tiempo == 'vence_hoy':
            contadores['vence_hoy'] += 1
            pedidos_urgentes.append(pedido)
        elif estado_tiempo == 'vence_pronto':
            contadores['vence_pronto'] += 1
        elif estado_tiempo == 'normal':
            contadores['normales'] += 1
        else:
            contadores['sin_iniciar'] += 1
    
    # Productos más rentados
    from django.db.models import Sum, Count
    productos_populares = DetallePedido.objects.filter(
        pedido__estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
    ).values(
        'producto__nombre'
    ).annotate(
        total_cantidad=Sum('cantidad'),
        total_pedidos=Count('pedido', distinct=True)
    ).order_by('-total_cantidad')[:5]
    
    # Ingresos por rentas activas
    ingresos_activos = pedidos_activos.aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Calcular porcentajes para las barras de progreso
    porcentajes = {}
    if total_activos > 0:
        porcentajes = {
            'vencidos': round((contadores['vencidos'] / total_activos) * 100, 1),
            'vence_hoy': round((contadores['vence_hoy'] / total_activos) * 100, 1),
            'vence_pronto': round((contadores['vence_pronto'] / total_activos) * 100, 1),
            'normales': round((contadores['normales'] / total_activos) * 100, 1),
            'sin_iniciar': round((contadores['sin_iniciar'] / total_activos) * 100, 1),
        }
    else:
        porcentajes = {
            'vencidos': 0,
            'vence_hoy': 0,
            'vence_pronto': 0,
            'normales': 0,
            'sin_iniciar': 0,
        }
    
    context = {
        'contadores': contadores,
        'porcentajes': porcentajes,
        'total_activos': total_activos,
        'pedidos_urgentes': pedidos_urgentes[:10],  # Solo los primeros 10
        'productos_populares': productos_populares,
        'ingresos_activos': ingresos_activos,
        'porcentaje_urgentes': round((contadores['vencidos'] + contadores['vence_hoy']) / max(total_activos, 1) * 100, 1),
    }
    
    return render(request, 'pedidos/dashboard_tiempo.html', context)
