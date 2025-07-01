import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django import forms
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from pedidos.models import Pedido, DetallePedido
from productos.models import Producto
from recibos.models import ReciboObra
from .forms import (UsuarioForm, ClienteForm, DireccionForm, EmpleadoCreationForm,
                    EmpleadoUpdateForm, CambiarPasswordEmpleadoForm, RegistroForm) # Asegúrate de que RegistroForm venga de aquí o defínelo aquí.
from .models import Usuario, Cliente, MetodoPago, Direccion, CarritoItem
from .models_divipola import Departamento, Municipio

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import mm, inch, cm

from datetime import datetime, timedelta
import os
import uuid
import io

# --- Funciones de Ayuda ---
def es_administrador(user):
    """Función para verificar si un usuario es administrador"""
    return user.is_authenticated and (user.tiene_permisos_admin() if hasattr(user, 'tiene_permisos_admin') else False)

# --- Vistas Generales y de Autenticación ---

def inicio_cliente(request):
    """Vista para la página de inicio de clientes"""
    productos_destacados = Producto.objects.filter(cantidad_disponible__gt=0).order_by('-id_producto')[:6]
    return render(request, 'usuarios/inicio_cliente.html', {
        'productos_destacados': productos_destacados
    })

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                # Si el usuario es cliente, crea el objeto Cliente relacionado solo si no existe
                if usuario.rol == 'cliente':
                    # Verificar si ya existe un cliente para este usuario
                    cliente, created = Cliente.objects.get_or_create(
                        usuario=usuario,
                        defaults={
                            'telefono': form.cleaned_data.get('telefono', ''),
                            'direccion': form.cleaned_data.get('direccion', '')
                        }
                    )
                    if not created:
                        # Si el cliente ya existía, actualizamos los datos
                        cliente.telefono = form.cleaned_data.get('telefono', cliente.telefono)
                        cliente.direccion = form.cleaned_data.get('direccion', cliente.direccion)
                        cliente.save()
                
                login(request, usuario)
                messages.success(request, '¡Registro exitoso! Bienvenido a MultiAndamios.')
                return redirect('usuarios:inicio_cliente')
                
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
                # No redirigir, mostrar el formulario con errores
        else:
            messages.error(request, 'Hubo errores en el formulario de registro. Por favor, corrígelos.')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

def iniciar_sesion(request):
    mensaje = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('usuarios:inicio_cliente')
        else:
            mensaje = 'Usuario o contraseña incorrectos.'
            messages.error(request, mensaje)
    return render(request, 'usuarios/login.html', {'mensaje': mensaje})

def cerrar_sesion(request):
    """
    Cierra la sesión del usuario y redirecciona a la página de inicio de clientes.
    Se consolida la funcionalidad de `logout_view`.
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:inicio_cliente')

def inicio(request):
    return render(request, 'usuarios/inicio.html')

def productos(request):
    productos = Producto.objects.all()
    return render(request, 'usuarios/productos.html', {'productos': productos})

# --- Vistas del Carrito de Compras ---

@login_required
def agregar_al_carrito(request, producto_id):
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('productos:detalle_producto', producto_id=producto_id)
    
    try:
        producto = Producto.objects.get(id_producto=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        dias_renta = int(request.POST.get('dias_renta', producto.dias_minimos_renta))
        
        if cantidad <= 0 or dias_renta <= 0:
            messages.error(request, 'La cantidad y los días de renta deben ser valores positivos.')
            return redirect('productos:detalle_producto', producto_id=producto_id)

        if producto.cantidad_disponible < cantidad:
            messages.error(request, f'Solo hay {producto.cantidad_disponible} unidades disponibles de {producto.nombre}.')
            return redirect('productos:detalle_producto', producto_id=producto_id)
        
        # Verificar que los días sean válidos para este producto
        if not producto.es_dias_valido(dias_renta):
            messages.error(request, f'Los días de renta deben ser múltiplos de {producto.dias_minimos_renta}.')
            return redirect('productos:detalle_producto', producto_id=producto_id)
        
        carrito_item, created = CarritoItem.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={
                'cantidad': cantidad,
                'dias_renta': dias_renta
            }
        )
        
        if not created:
            # Si el item ya existía, actualizar los valores
            carrito_item.cantidad = cantidad
            carrito_item.dias_renta = dias_renta
            carrito_item.save()
        
        messages.success(request, f'{producto.nombre} agregado al carrito para renta por {dias_renta} día{"s" if dias_renta > 1 else ""}.')
        
    except Producto.DoesNotExist:
        messages.error(request, 'El producto seleccionado no existe.')
    except ValueError:
        messages.error(request, 'Cantidad o días de renta inválidos. Asegúrate de ingresar números enteros.')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al agregar al carrito: {str(e)}')
    
    return redirect('usuarios:ver_carrito')

@login_required
def ver_carrito(request):
    """Vista para ver el contenido del carrito"""
    items_carrito = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    total = sum(item.subtotal for item in items_carrito)
    peso_total = sum(item.peso_total for item in items_carrito)
    
    context = {
        'items_carrito': items_carrito,
        'total': total,
        'peso_total': peso_total,
    }
    return render(request, 'usuarios/carrito.html', context)

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    
    # Si el item estaba reservado, liberar la reserva
    if item.reservado:
        item.liberar_reserva() # Asumiendo que este método existe y maneja la devolución al inventario
    
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('usuarios:ver_carrito')

@login_required
def limpiar_carrito(request):
    """Vista para limpiar todos los items del carrito"""
    items = CarritoItem.objects.filter(usuario=request.user)
    
    with transaction.atomic(): # Asegura que si algo falla, no se limpien parcialmente los items
        for item in items:
            if item.reservado:
                item.liberar_reserva() # Asegúrate de que esta función exista en tu modelo CarritoItem
            item.delete()
    
    messages.success(request, "Se ha limpiado el carrito exitosamente.")
    return redirect('usuarios:ver_carrito')

@csrf_exempt # Considera cuidadosamente el uso en producción; idealmente, usa tokens CSRF.
def actualizar_carrito(request):
    """
    Esta vista maneja la lógica para actualizar la cantidad o meses de renta
    de un ítem en el carrito de compras (DetallePedido).
    Espera una solicitud POST con datos JSON:
    {
        "detalle_pedido_id": <int>,
        "cantidad": <int, opcional>,
        "meses_renta": <int, opcional>
    }
    Si la cantidad es 0, el DetallePedido será eliminado.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle_pedido_id = data.get('detalle_pedido_id')
            nueva_cantidad = data.get('cantidad')
            nuevos_meses_renta = data.get('meses_renta')

            if not detalle_pedido_id:
                return JsonResponse({'success': False, 'message': 'Se requiere el ID del detalle del pedido.'}, status=400)

            try:
                detalle_pedido = DetallePedido.objects.select_related('pedido').get(id=detalle_pedido_id)
            except DetallePedido.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Ítem del carrito no encontrado.'}, status=404)

            # Usamos una transacción para asegurar que todas las operaciones se completen
            # o se reviertan si algo falla.
            with transaction.atomic():
                # 1. Actualizar la cantidad si se proporciona y es válida
                if nueva_cantidad is not None:
                    if not isinstance(nueva_cantidad, int) or nueva_cantidad < 0:
                        return JsonResponse({'success': False, 'message': 'Cantidad inválida. Debe ser un número entero no negativo.'}, status=400)
                    detalle_pedido.cantidad = nueva_cantidad

                # 2. Actualizar los meses de renta si se proporcionan y son válidos
                if nuevos_meses_renta is not None:
                    if not isinstance(nuevos_meses_renta, int) or nuevos_meses_renta < 1:
                        return JsonResponse({'success': False, 'message': 'Meses de renta inválidos. Debe ser un número entero positivo.'}, status=400)
                    detalle_pedido.meses_renta = nuevos_meses_renta

                # Validar la cantidad contra el stock disponible ANTES de guardar
                # Esto es importante si el modelo DetallePedido.clean() no lo maneja completamente antes del save.
                # Tu modelo ya lo tiene en clean(), lo cual es genial, pero una verificación temprana no hace daño.
                # if detalle_pedido.producto.cantidad_disponible < detalle_pedido.cantidad:
                #     return JsonResponse({'success': False, 'message': f'No hay suficiente stock para {detalle_pedido.producto.nombre}. Disponible: {detalle_pedido.producto.cantidad_disponible}'}, status=400)

                # 3. Eliminar el ítem si la cantidad es 0
                if detalle_pedido.cantidad == 0:
                    detalle_pedido.delete()
                    # Recalcular el total del Pedido después de la eliminación
                    pedido_afectado = detalle_pedido.pedido
                    # Asegurarse de que el subtotal del pedido refleje los cambios
                    pedido_afectado.subtotal = sum(dp.subtotal for dp in pedido_afectado.detalles.all())
                    pedido_afectado.save() # Esto llamará a update_total() y full_clean() en el Pedido
                    return JsonResponse({'success': True, 'message': 'Ítem eliminado del carrito.',
                                         'pedido_id': pedido_afectado.id_pedido,
                                         'nuevo_subtotal_pedido': str(pedido_afectado.subtotal),
                                         'nuevo_iva_pedido': str(pedido_afectado.iva),
                                         'nuevo_total_pedido': str(pedido_afectado.total)
                                         })

                # 4. Guardar los cambios en el DetallePedido (recalculará su subtotal automáticamente)
                try:
                    detalle_pedido.save() # La validación .clean() y el cálculo de subtotal ocurrirán aquí
                except ValidationError as e:
                    return JsonResponse({'success': False, 'message': str(e)}, status=400)

                # 5. Actualizar el subtotal y total del Pedido principal (carrito)
                # Tu modelo Pedido.save() ya llama a update_total(), así que solo necesitamos guardar el pedido
                pedido_afectado = detalle_pedido.pedido
                # Recalcular el subtotal del pedido sumando los subtotales de sus detalles
                # (excluyendo el propio detalle_pedido si no se actualizó su subtotal antes de sumarlo)
                # Para mayor seguridad, volvemos a calcular el subtotal del pedido
                pedido_afectado.subtotal = sum(dp.subtotal for dp in pedido_afectado.detalles.all())
                pedido_afectado.save() # Esto llamará a update_total() y full_clean() en el Pedido

                return JsonResponse({'success': True, 'message': 'Carrito actualizado exitosamente.',
                                     'detalle_pedido_id': detalle_pedido.id,
                                     'nueva_cantidad': detalle_pedido.cantidad,
                                     'nuevos_meses_renta': detalle_pedido.meses_renta,
                                     'nuevo_subtotal_item': str(detalle_pedido.subtotal), # Convertir Decimal a str
                                     'pedido_id': pedido_afectado.id_pedido,
                                     'nuevo_subtotal_pedido': str(pedido_afectado.subtotal), # Convertir Decimal a str
                                     'nuevo_iva_pedido': str(pedido_afectado.iva),
                                     'nuevo_total_pedido': str(pedido_afectado.total)
                                     })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato JSON inválido.'}, status=400)
        except Exception as e:
            # Captura cualquier otra excepción inesperada
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido. Use POST.'}, status=405)


# --- Generación de PDFs (Refactorizado) ---

# Información común para el emisor
EMISOR_INFO = {
    'nombre': 'MULTIANDAMIOS S.A.S.',
    'nif': 'NIT 900.252.510-1',
    'direccion': 'Cra. 128 #22A-45, Bogotá, Colombia',
    'telefono': '+57 310 574 2020',
    'email': 'info@multiandamios.co'
}

def _draw_pdf_header(p, width, height, title):
    """Dibuja el encabezado de la página para cotizaciones y remisiones."""
    p.setFillColor(colors.HexColor("#FFD600"))
    p.rect(0, height - 60, width, 60, fill=1, stroke=0)
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(width / 2, height - 40, title)
    
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 50, height - 55, "MULTIANDAMIOS S.A.S.")

def _draw_info_section(p, y_start, width, emisor, receptor):
    """Dibuja la sección de datos del proveedor y cliente."""
    p.setLineWidth(0.5)
    p.rect(40, y_start - 160, width - 80, 140, stroke=1, fill=0) # Marco para información
    
    # Títulos de secciones
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y_start - 15, "DATOS DEL PROVEEDOR")
    p.drawString(width / 2 + 10, y_start - 15, "DATOS DEL CLIENTE")
    
    # Información del emisor
    current_y_emisor = y_start - 35
    p.setFont("Helvetica", 10)
    for key, value in emisor.items():
        label = key.upper() + ": "
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, current_y_emisor, label)
        p.setFont("Helvetica", 9)
        p.drawString(50 + p.stringWidth(label, "Helvetica-Bold", 9), current_y_emisor, value)
        current_y_emisor -= 15
    
    # Información del receptor
    current_y_receptor = y_start - 115
    for key, value in receptor.items():
        label = key.upper() + ": "
        p.setFont("Helvetica-Bold", 9)
        p.drawString(width / 2 + 10, current_y_receptor, label)
        p.setFont("Helvetica", 9)
        str_value = str(value) if value is not None else "N/A"
        p.drawString(width / 2 + 10 + p.stringWidth(label, "Helvetica-Bold", 9), current_y_receptor, str_value)
        current_y_receptor -= 15
    return current_y_emisor # Retorna la Y actual después de dibujar la sección

def _draw_table_header(p, headers, x, y, col_widths, row_height=20):
    """Dibuja el encabezado de la tabla."""
    p.setFillColor(colors.HexColor("#F5F5F5"))
    p.rect(x, y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    current_x = x
    for i, header in enumerate(headers):
        p.drawString(current_x + 5, y - 15, header)
        current_x += col_widths[i]
    return y - row_height

def _generate_common_pdf(request, document_type, items_to_include):
    """
    Función genérica para generar PDFs de cotización o remisión.
    :param document_type: 'cotizacion' o 'remision'
    :param items_to_include: QuerySet de CarritoItem (para cotización) o items reservados (para remisión)
    """
    if not items_to_include.exists():
        messages.error(request, f'El carrito está vacío o no hay items reservados para la {document_type}.')
        return redirect('usuarios:ver_carrito') # O a donde sea más apropiado

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document_type}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Información del receptor (cliente)
    user = request.user
    receptor_info = {
        'nombre': f"{user.first_name} {user.last_name}".strip() or "N/A",
        'nif': str(getattr(user, 'numero_identidad', 'N/A')),
        'direccion': str(getattr(user, 'direccion', 'N/A')), # Asumiendo que 'direccion' está en el modelo Usuario
        'telefono': str(getattr(user, 'telefono', 'N/A')), # Asumiendo que 'telefono' está en el modelo Usuario
        'email': str(user.email or 'N/A')
    }

    # Primera página
    _draw_pdf_header(p, width, height, document_type.upper())
    y = height - 80 # Posición inicial para la sección de información
    
    _draw_info_section(p, y, width, EMISOR_INFO, receptor_info)

    # Información del documento (cotización/remisión)
    y_after_info_box = height - 200 # Ajustar la Y después de la caja de información
    p.setFont("Helvetica", 10)
    fecha = datetime.now()
    p.drawString(50, y_after_info_box, f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(width - 200, y_after_info_box, f"{document_type.capitalize()} #: {uuid.uuid4().hex[:8].upper()}") # Número aleatorio

    # Tabla de productos
    y_table_start = y_after_info_box - 40
    headers = ["Descripción", "Cant.", "Período", "Precio Unit.", "Subtotal"]
    col_widths = [250, 60, 60, 80, 80]
    row_height = 20

    current_y = _draw_table_header(p, headers, 40, y_table_start, col_widths)
    
    p.setFont("Helvetica", 9)
    total_sin_iva = Decimal('0.00')
    peso_total = Decimal('0.00')

    for item in items_to_include:
        if current_y < 100: # Nueva página si no hay espacio suficiente para una fila y el pie
            p.showPage()
            _draw_pdf_header(p, width, height, document_type.upper())
            current_y = height - 100 # Reinicia Y para el encabezado de la tabla en la nueva página
            current_y = _draw_table_header(p, headers, 40, current_y, col_widths)
            p.setFont("Helvetica", 9)

        subtotal = item.subtotal
        total_sin_iva += subtotal
        peso_total += item.peso_total  # Now both are Decimal types
        
        # Dibujar fondo de la fila
        p.setFillColor(colors.white)
        p.rect(40, current_y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
        p.setFillColor(colors.black)
        
        # Datos de la fila
        x = 40
        precio_unitario = item.producto.precio_diario
        duracion_texto = item.get_descripcion_dias()
        
        row_data = [
            item.producto.nombre[:40],
            str(item.cantidad),
            duracion_texto,
            f"${precio_unitario:,.2f}",
            f"${subtotal:,.2f}"
        ]
        
        for i, text in enumerate(row_data):
            p.drawString(x + 5, current_y - 15, text)
            x += col_widths[i]
        
        current_y -= row_height

    # Totales y Peso Total
    current_y -= 20
    p.setFont("Helvetica-Bold", 10)
    
    if document_type == 'remision':
        p.drawString(50, current_y, f"Peso total: {peso_total:.2f} kg")
        current_y -= 20 # Espacio para el peso total en remisión

    iva = (total_sin_iva * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_con_iva = total_sin_iva + iva

    # Dibujar recuadro para totales
    p.setFillColor(colors.HexColor("#F5F5F5"))
    totals_x = width - 250
    p.rect(totals_x, current_y - 60, 200, 60, fill=1, stroke=1)
    p.setFillColor(colors.black)

    # Mostrar totales
    p.drawString(totals_x + 10, current_y - 20, f"Subtotal: ${total_sin_iva:,.2f}")
    p.drawString(totals_x + 10, current_y - 40, f"IVA (19%): ${iva:,.2f}")
    p.setFillColor(colors.HexColor("#FFD600"))
    p.rect(totals_x, current_y - 60, 200, 20, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.drawString(totals_x + 10, current_y - 55, f"Total: ${total_con_iva:,.2f}")

    # Observaciones (Solo para cotización)
    if document_type == 'cotizacion':
        current_y -= 90
        p.setFont("Helvetica", 9)
        p.drawString(40, current_y, "OBSERVACIONES:")
        current_y -= 15
        p.drawString(40, current_y, "• Esta cotización tiene validez de 15 días.")
        current_y -= 15
        p.drawString(40, current_y, "• Los precios incluyen IVA del 19%.")
        current_y -= 15
        p.drawString(40, current_y, "• El costo del transporte no está incluido y depende de la zona de entrega.")
        current_y -= 15
        p.drawString(40, current_y, "• Forma de pago: Contra entrega o transferencia bancaria.")
    else: # Espacio para remisión si no hay observaciones
        current_y -= 60


    # Firmas
    current_y -= 40
    p.line(50, current_y, 250, current_y)
    p.line(width-250, current_y, width-50, current_y)
    p.setFont("Helvetica", 10)
    p.drawCentredString(150, current_y - 20, "Firma del Cliente")
    p.drawCentredString(width - 150, current_y - 20, "Firma del Proveedor")

    # Pie de página
    p.setFont("Helvetica", 8)
    p.drawString(40, 30, "MULTIANDAMIOS S.A.S. - Servicio al cliente: +57 310 574 2020")
    p.drawString(40, 20, "Email: info@multiandamios.co | www.multiandamios.co")
    
    p.save()
    return response

@login_required
def generar_cotizacion_pdf(request):
    try:
        items_carrito = CarritoItem.objects.filter(usuario=request.user)
        return _generate_common_pdf(request, 'cotizacion', items_carrito)
    except Exception as e:
        messages.error(request, f'Error al generar la cotización: {str(e)}')
        return redirect('usuarios:ver_carrito')

@login_required
def generar_remision_pdf(request):
    try:
        # Aquí asumo que la remisión se genera solo para items que ya han sido 'reservados'
        # Esto podría estar ligado a un pedido ya confirmado o a una etapa previa.
        # Asegúrate de que esta lógica de `reservado=True` sea coherente con tu flujo de negocio.
        items_remision = CarritoItem.objects.filter(usuario=request.user, reservado=True).select_related('producto')
        if not items_remision.exists():
            messages.warning(request, 'No hay productos reservados para generar la remisión. Asegúrate de haber completado un pedido.')
            return redirect('usuarios:ver_carrito') # O a la vista de pedidos

        return _generate_common_pdf(request, 'remision', items_remision)
    except Exception as e:
        messages.error(request, f'Error al generar la remisión: {str(e)}')
        return redirect('usuarios:ver_carrito')


# --- Vistas del Perfil de Usuario ---

@login_required
def perfil(request):
    """Vista para mostrar el perfil del usuario"""
    # Obtener o crear el cliente asociado al usuario
    # Es crucial que un Cliente SIEMPRE exista si un Usuario es de rol 'cliente'
    cliente, created = Cliente.objects.get_or_create(
        usuario=request.user,
        defaults={
            'telefono': request.user.telefono if hasattr(request.user, 'telefono') else '',
            'direccion': request.user.direccion if hasattr(request.user, 'direccion') else ''
        }
    )
    
    direcciones = Direccion.objects.filter(usuario=request.user)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    
    context = {
        'cliente': cliente,
        'direcciones': direcciones,
        'pedidos': pedidos
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def actualizar_perfil(request):
    """Vista para actualizar la información del perfil"""
    # Obtener o crear el cliente asociado al usuario
    cliente, created = Cliente.objects.get_or_create(
        usuario=request.user,
        defaults={
            'telefono': getattr(request.user, 'telefono', ''),
            'direccion': getattr(request.user, 'direccion', '')
        }
    )
    
    if created:
        messages.info(request, 'Se ha creado tu perfil de cliente automáticamente.')
    
    if request.method == 'POST':
        # Instanciar formularios con los datos del POST y las instancias existentes
        usuario_form = UsuarioForm(request.POST, instance=request.user)
        cliente_form = ClienteForm(request.POST, instance=cliente)
        
        if usuario_form.is_valid() and cliente_form.is_valid():
            usuario_form.save()
            cliente_form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Hubo errores al actualizar el perfil. Por favor, corrige los campos.')
            # Si hay errores, los formularios contendrán los mensajes de error
            context = {
                'usuario_form': usuario_form,
                'cliente_form': cliente_form,
                'usuario': request.user, # Mantener para referencia en template si se requiere
                'cliente': cliente
            }
            return render(request, 'usuarios/actualizar_perfil.html', context)
    else:
        # Para GET, instanciar formularios con los datos existentes
        usuario_form = UsuarioForm(instance=request.user)
        cliente_form = ClienteForm(instance=cliente)
    
    context = {
        'usuario_form': usuario_form,
        'cliente_form': cliente_form,
        'usuario': request.user,
        'cliente': cliente
    }
    return render(request, 'usuarios/actualizar_perfil.html', context)

@login_required
def cambiar_contrasena(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # Importante para mantener la sesión activa
            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores indicados al cambiar la contraseña.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'usuarios/cambiar_contrasena.html', {
        'form': form
    })

@login_required
def agregar_direccion(request):
    """Vista para agregar una nueva dirección"""
    # Ensure cliente exists
    cliente, created = Cliente.objects.get_or_create(
        usuario=request.user,
        defaults={
            'telefono': getattr(request.user, 'telefono', ''),
            'direccion': getattr(request.user, 'direccion', '')
        }
    )
    departamentos = Departamento.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.usuario = request.user  # Use usuario field instead of cliente
            direccion.save()
            
            # Si esta dirección es marcada como principal, actualizar las demás
            if direccion.principal:  # Use 'principal' instead of 'es_principal'
                Direccion.objects.filter(usuario=request.user).exclude(id=direccion.id).update(principal=False)
            
            messages.success(request, 'Dirección agregada exitosamente.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Hubo errores al agregar la dirección. Por favor, verifica los campos.')
    else:
        form = DireccionForm()
    
    return render(request, 'usuarios/agregar_direccion.html', {
        'form': form,
        'departamentos': departamentos
    })

@login_required
def editar_direccion(request, direccion_id):
    """Vista para editar una dirección existente"""
    direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
    departamentos = Departamento.objects.all().order_by('nombre')
    municipios = Municipio.objects.filter(departamento=direccion.departamento).order_by('nombre')

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            direccion = form.save(commit=False)
            principal_nueva = form.cleaned_data.get('principal')
            
            # Si se marca como principal y no lo era, o si se desmarca
            if principal_nueva and not direccion.principal:
                Direccion.objects.filter(usuario=direccion.usuario).update(principal=False)
            direccion.principal = principal_nueva
            
            direccion.save()
            messages.success(request, 'Dirección actualizada exitosamente.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Hubo errores al editar la dirección. Por favor, corrige los campos.')
    else:
        form = DireccionForm(instance=direccion)
    
    return render(request, 'usuarios/editar_direccion.html', {
        'direccion': direccion,
        'form': form,
        'departamentos': departamentos,
        'municipios': municipios # Para precargar los municipios del departamento seleccionado
    })

@login_required
def eliminar_direccion(request, direccion_id):
    """Vista para eliminar una dirección"""
    direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
    
    # No permitir eliminar la única dirección principal
    if direccion.principal and Direccion.objects.filter(usuario=direccion.usuario).count() == 1:
        messages.error(request, 'No puedes eliminar tu única dirección principal. Debes tener al menos una dirección principal.')
        return redirect('usuarios:perfil')
    
    with transaction.atomic():
        # Si se elimina la dirección principal, establecer otra como principal
        if direccion.principal:
            # Encuentra la primera dirección NO eliminada que no sea la actual
            nueva_principal = Direccion.objects.filter(usuario=direccion.usuario).exclude(id=direccion.id).first()
            if nueva_principal:
                nueva_principal.principal = True
                nueva_principal.save()
        
        direccion.delete()
        messages.success(request, 'Dirección eliminada exitosamente.')
    return redirect('usuarios:perfil')

# --- Vistas de Checkout y Pedidos ---

@login_required
def checkout(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    if not carrito_items.exists():
        messages.error(request, 'Tu carrito está vacío. Agrega productos antes de proceder al pago.')
        return redirect('usuarios:ver_carrito')
    
    departamentos = Departamento.objects.all().order_by('nombre')

    subtotal = sum(item.subtotal for item in carrito_items)
    iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Get transport cost from first item's municipality (assuming all items to same location)
    costo_transporte = Decimal('0.00')
    if carrito_items.first() and hasattr(carrito_items.first().producto, 'categoria'):
        # Default transport cost if not specified
        costo_transporte = Decimal('10000.00')  # Default 10,000 COP
    
    total_pedido = subtotal + iva + costo_transporte

    context = {
        'items': carrito_items,
        'departamentos': departamentos,
        'subtotal': subtotal,
        'iva': iva,
        'costo_transporte': costo_transporte,
        'total': total_pedido,
    }

    if request.method == 'POST':
        # Se asume que el formulario HTML envía los datos de la dirección y pago
        departamento_id = request.POST.get('departamento')
        municipio_id = request.POST.get('municipio')
        codigo_divipola = request.POST.get('codigo_divipola')
        codigo_postal = request.POST.get('codigo_postal')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento', '')
        notas = request.POST.get('notas', '')

        # Validación de campos básicos de la dirección
        if not all([departamento_id, municipio_id, codigo_divipola, calle, numero]):
            messages.error(request, 'Por favor, complete todos los campos obligatorios de la dirección de envío.')
            return render(request, 'usuarios/checkout.html', context)
        
        try:
            with transaction.atomic():
                # 1. Obtener la información completa de la dirección DIVIPOLA
                departamento = get_object_or_404(Departamento, id=departamento_id)
                municipio = get_object_or_404(Municipio, id=municipio_id)
                
                # 2. Determinar la dirección de envío (se puede crear o usar una existente)
                # Si prefieres usar una dirección existente del cliente, la lógica debería ser diferente
                
                # Asegurar que el cliente existe, crear si no existe
                cliente, created_cliente = Cliente.objects.get_or_create(
                    usuario=request.user,
                    defaults={
                        'telefono': getattr(request.user, 'telefono', ''),
                        'direccion': getattr(request.user, 'direccion', '')
                    }
                )
                
                if created_cliente:
                    messages.info(request, 'Se ha creado tu perfil de cliente automáticamente.')
                
                direccion_envio, created_direccion = Direccion.objects.get_or_create(
                    usuario=request.user,  # Use usuario instead of cliente
                    calle=calle,
                    numero=numero,
                    complemento=complemento,
                    departamento=departamento,
                    municipio=municipio,
                    codigo_divipola=codigo_divipola,
                    codigo_postal=codigo_postal,
                    defaults={'principal': False} # Use 'principal' instead of 'es_principal'
                )
                
                # 3. Crear el Pedido con totales calculados
                pedido = Pedido.objects.create(
                    cliente=cliente,
                    subtotal=subtotal,
                    iva=iva,
                    costo_transporte=costo_transporte,
                    total=total_pedido,
                    estado_pedido_general='pendiente_pago',
                    notas=notas,
                    direccion_entrega=f"{calle} #{numero} {complemento}, {municipio.nombre}, {departamento.nombre}".strip()
                )

                # 4. Procesar los items del carrito para crear DetallePedido y actualizar inventario
                for item in carrito_items:
                    # Descontar del inventario
                    producto = item.producto
                    if producto.cantidad_disponible < item.cantidad:
                        raise ValidationError(f'No hay suficientes unidades de {producto.nombre} disponibles.')
                    
                    producto.cantidad_disponible -= item.cantidad
                    producto.save()

                    # Crear DetallePedido
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_diario=item.producto.precio_diario,
                        dias_renta=item.dias_renta,
                        subtotal=item.subtotal
                    )
                    # Marcar el item del carrito como 'reservado' o 'procesado' si no se elimina inmediatamente
                    # Si los items se eliminan del carrito, no es necesario marcarlos como reservados aquí.
                    # Asumo que 'reservado' es para la remisión, pero en un checkout exitoso se borrarían.
                    item.delete() # Eliminar el item del carrito después de procesarlo
                
                messages.success(request, f'Tu pedido #{pedido.id_pedido} ha sido creado exitosamente.')
                
                # Redirect to payment processing
                return redirect('usuarios:procesar_pago', pedido_id=pedido.id_pedido)

        except ValidationError as e:
            messages.error(request, f'Error en el pedido: {e.message}')
            # Si hay un error, revertir cualquier cambio en el carrito (bandera en_proceso_pago)
            for item in carrito_items:
                item.en_proceso_pago = False
                item.save()
            return render(request, 'usuarios/checkout.html', context)
        except Producto.DoesNotExist:
            messages.error(request, 'Uno de los productos en tu carrito no existe. Por favor, revisa tu carrito.')
            for item in carrito_items:
                item.en_proceso_pago = False
                item.save()
            return render(request, 'usuarios/checkout.html', context)
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento seleccionado no es válido.')
            for item in carrito_items:
                item.en_proceso_pago = False
                item.save()
            return render(request, 'usuarios/checkout.html', context)
        except Municipio.DoesNotExist:
            messages.error(request, 'El municipio seleccionado no es válido.')
            for item in carrito_items:
                item.en_proceso_pago = False
                item.save()
            return render(request, 'usuarios/checkout.html', context)
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado al procesar tu pedido: {str(e)}')
            # Es importante que si algo falla, los items del carrito no queden en un estado intermedio
            for item in carrito_items:
                item.en_proceso_pago = False
                item.save()
            return render(request, 'usuarios/checkout.html', context)
    
    # Para la primera carga del formulario o si hay errores de validación
    return render(request, 'usuarios/checkout.html', context)

# Vista para cargar municipios basada en el departamento seleccionado (AJAX)
def cargar_municipios(request):
    departamento_id = request.GET.get('departamento_id')
    municipios = []
    if departamento_id:
        try:
            municipios = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre').values('id', 'nombre', 'codigo_divipola')
        except Exception as e:
            # Manejo de error si el ID del departamento no es válido
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse(list(municipios), safe=False)

# Vista para obtener el código DIVIPOLA de un municipio (AJAX)
def obtener_codigo_divipola(request):
    municipio_id = request.GET.get('municipio_id')
    codigo_divipola = ''
    if municipio_id:
        try:
            municipio = Municipio.objects.get(id=municipio_id)
            codigo_divipola = municipio.codigo_divipola
        except Municipio.DoesNotExist:
            return JsonResponse({'error': 'Municipio no encontrado'}, status=404)
    return JsonResponse({'codigo_divipola': codigo_divipola})

@login_required
def pedidos_pendientes(request):
    """Vista para mostrar pedidos pendientes de pago del usuario"""
    from pedidos.models import Pedido
    
    # Get pending orders for the current user
    pedidos_pendientes = Pedido.objects.filter(
        cliente__usuario=request.user,
        estado_pedido_general__in=['pendiente_pago', 'procesando_pago', 'pago_vencido', 'pago_rechazado']
    ).order_by('-fecha')
    
    context = {
        'pedidos': pedidos_pendientes,
        'titulo': 'Pedidos Pendientes'
    }
    
    return render(request, 'usuarios/pedidos_pendientes.html', context)

def lista_clientes(request):
    """
    Esta es la vista para mostrar la lista de clientes.
    Aquí podrías obtener los datos de tus clientes de la base de datos
    y pasarlos a una plantilla.
    """
    # Por ahora, solo devolveremos una respuesta simple para verificar que funciona
    return HttpResponse("<h1>¡Página de Lista de Clientes!</h1>")

def crear_cliente(request):
    """
    Esta es la vista para crear un nuevo cliente.
    Aquí iría la lógica para manejar el formulario de creación de clientes.
    """
    # Por ahora, solo devolveremos una respuesta simple
    return HttpResponse("<h1>¡Formulario para Crear un Nuevo Cliente!</h1>")

@login_required
def actualizar_carrito(request):
    """
    Vista para actualizar el carrito de compras vía formulario.
    Actualiza cantidades, períodos de renta y tipos de renta sin redireccionar.
    """
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener todos los items del carrito del usuario
                items_carrito = CarritoItem.objects.filter(usuario=request.user)
                
                items_actualizados = 0
                errores = []
                
                for item in items_carrito:
                    item_id = str(item.id)
                    
                    # Verificar si hay datos para este item
                    cantidad_key = f'cantidad_{item_id}'
                    dias_key = f'dias_{item_id}'
                    
                    # Actualizar cantidad si está presente
                    if cantidad_key in request.POST:
                        try:
                            nueva_cantidad = int(request.POST[cantidad_key])
                            if nueva_cantidad > 0:
                                if nueva_cantidad <= item.producto.cantidad_disponible:
                                    item.cantidad = nueva_cantidad
                                    items_actualizados += 1
                                else:
                                    errores.append(f'Solo hay {item.producto.cantidad_disponible} unidades disponibles de {item.producto.nombre}')
                                    continue
                            else:
                                errores.append(f'La cantidad debe ser mayor a 0 para {item.producto.nombre}')
                                continue
                        except (ValueError, TypeError):
                            errores.append(f'Cantidad inválida para {item.producto.nombre}')
                            continue
                    
                    # Actualizar días de renta si está presente
                    if dias_key in request.POST:
                        try:
                            nuevos_dias = int(request.POST[dias_key])
                            if nuevos_dias > 0:
                                if item.producto.es_dias_valido(nuevos_dias):
                                    item.dias_renta = nuevos_dias
                                    items_actualizados += 1
                                else:
                                    errores.append(f'Los días deben ser múltiplos de {item.producto.dias_minimos_renta} para {item.producto.nombre}')
                                    continue
                            else:
                                errores.append(f'Los días de renta deben ser mayor a 0 para {item.producto.nombre}')
                                continue
                        except (ValueError, TypeError):
                            errores.append(f'Días de renta inválidos para {item.producto.nombre}')
                            continue
                    
                    # Guardar el item actualizado
                    item.save()
                
                # Si es una petición AJAX, devolver JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    if errores:
                        return JsonResponse({
                            'success': False,
                            'message': 'Se encontraron errores al actualizar el carrito',
                            'errors': errores
                        })
                    else:
                        return JsonResponse({
                            'success': True,
                            'message': f'Carrito actualizado exitosamente. {items_actualizados} elementos modificados.',
                            'items_updated': items_actualizados
                        })
                
                # Para peticiones normales, mostrar mensajes y redireccionar
                if errores:
                    for error in errores:
                        messages.error(request, error)
                else:
                    if items_actualizados > 0:
                        messages.success(request, f'Carrito actualizado exitosamente. {items_actualizados} elementos modificados.')
                    else:
                        messages.info(request, 'No se realizaron cambios en el carrito.')
                
        except Exception as e:
            error_msg = f'Error al actualizar el carrito: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg})
            else:
                messages.error(request, error_msg)
    
    # Redireccionar de vuelta al carrito
    return redirect('usuarios:ver_carrito')

def generar_recibo_pdf(request, pedido_id):
    """
    Esta vista genera un recibo en formato PDF para un pedido específico.
    """
    # Aquí es donde iría la lógica para obtener los datos del pedido
    # y luego usar una librería como ReportLab o WeasyPrint para generar el PDF.

    # Ejemplo muy básico de cómo empezarías a generar un PDF (requiere ReportLab):
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="recibo_pedido_{pedido_id}.pdf"'
    #
    # p = canvas.Canvas(response, pagesize=letter)
    # p.drawString(100, 750, f"Recibo para Pedido #{pedido_id}")
    # p.showPage()
    # p.save()
    # return response

    # Por ahora, solo devolveremos una respuesta simple de texto para que el servidor se inicie.
    return HttpResponse(f"<h1>Simulando la generación de PDF para Pedido #{pedido_id}</h1>"
                        "<p>Aquí se generaría el recibo PDF.</p>")

def pago_recibo(request, pedido_id):
    """
    Esta vista manejará el proceso de pago para un recibo o pedido específico.
    """
    # Aquí iría la lógica para procesar el pago, interactuar con pasarelas de pago,
    # actualizar el estado del pedido, etc.
    if request.method == 'POST':
        # Lógica para procesar el pago enviado por formulario
        return HttpResponse(f"Procesando pago para Pedido #{pedido_id} (POST)")
    else:
        # Lógica para mostrar la página de pago o confirmación
        return HttpResponse(f"<h1>Página de Pago para Pedido #{pedido_id}</h1>"
                            "<p>Aquí iría el formulario de pago.</p>")
    
def confirmacion_pago(request, pedido_id):
    """
    Esta vista muestra una página de confirmación después de un pago exitoso.
    """
    # Aquí puedes recuperar información del pedido o del pago para mostrarla al usuario.
    return HttpResponse(f"<h1>¡Pago Confirmado para Pedido #{pedido_id}!</h1>"
                        "<p>Gracias por tu compra.</p>")

def ver_remision(request, pedido_id):
    """
    Esta vista mostrará o generará una remisión para un pedido específico.
    Similar a un recibo, pero quizás con información diferente para propósitos de entrega/envío.
    """
    # Aquí iría la lógica para obtener los datos del pedido y de la remisión.
    # Podrías renderizar una plantilla HTML o incluso generar un PDF aquí mismo,
    # similar a generar_recibo_pdf.
    return HttpResponse(f"<h1>Remisión para Pedido #{pedido_id}</h1>"
                        "<p>Detalles de la remisión y entrega.</p>")

def generar_remision_admin(request, pedido_id):
    """
    Esta vista permite a los administradores o personal autorizado generar una remisión PDF.
    Podría requerir autenticación y permisos especiales.
    """
    # Aquí la lógica para obtener los datos del pedido y generar un PDF de remisión.
    # Es similar a generar_recibo_pdf, pero quizás con un formato diferente
    # y datos específicos para una remisión administrativa.
    return HttpResponse(f"<h1>Generando Remisión Admin para Pedido #{pedido_id}</h1>"
                        "<p>Esta es una función administrativa para generar remisiones.</p>")

@login_required
def get_precio_carrito_item(request, item_id):
    """
    Vista AJAX que devuelve el precio actualizado de un ítem del carrito
    cuando cambian los días de renta.
    """
    try:
        # Buscar el item del carrito
        item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
        
        # Obtener los días de renta de la query string
        dias_renta = int(request.GET.get('dias_renta', item.dias_renta))
        
        # Validar los días de renta
        if not item.producto.es_dias_valido(dias_renta):
            return JsonResponse({
                'success': False,
                'error': f'Los días deben ser múltiplos de {item.producto.dias_minimos_renta}'
            }, status=400)
        
        # Calcular el precio total
        precio_total = item.producto.get_precio_total(dias_renta, item.cantidad)
        
        return JsonResponse({
            'success': True,
            'item_id': item_id,
            'precio_diario': float(item.producto.precio_diario),
            'dias_renta': dias_renta,
            'precio_total': float(precio_total),
            'nombre_producto': item.producto.nombre
        })
        
    except CarritoItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Item del carrito no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)

@login_required
def procesar_pago(request, pedido_id):
    """Vista para procesar el pago de un pedido"""
    from pedidos.models import Pedido
    
    # Get the order and verify it belongs to the user
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente__usuario=request.user)
    
    # Verify order is in a payable state
    if pedido.estado_pedido_general not in ['pendiente_pago', 'pago_vencido', 'pago_rechazado']:
        messages.error(request, 'Este pedido no está disponible para pago.')
        return redirect('pedidos:mis_pedidos')
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        numero_referencia = request.POST.get('numero_referencia', '')
        comprobante = request.FILES.get('comprobante')
        
        if not metodo_pago:
            messages.error(request, 'Por favor selecciona un método de pago.')
            return render(request, 'usuarios/procesar_pago.html', {'pedido': pedido})
        
        # Additional validation for non-cash payments
        if metodo_pago in ['transferencia', 'tarjeta']:
            if not numero_referencia:
                messages.error(request, 'Por favor ingresa el número de referencia para este tipo de pago.')
                return render(request, 'usuarios/procesar_pago.html', {'pedido': pedido})
        
        try:
            with transaction.atomic():
                # Create payment method record
                metodo_pago_obj = MetodoPago.objects.create(
                    pedido=pedido,  # Associate payment with the order
                    usuario=request.user,
                    tipo=metodo_pago,
                    monto=pedido.total,
                    numero_referencia=numero_referencia,
                    comprobante=comprobante,
                    estado='pendiente'  # Will be approved by admin
                )
                
                # Update order with payment info
                pedido.metodo_pago = metodo_pago
                pedido.ref_pago = numero_referencia
                if metodo_pago == 'efectivo':
                    # Cash payments need admin approval
                    pedido.estado_pedido_general = 'procesando_pago'
                    messages.success(request, f'Tu pago en efectivo ha sido registrado. El pedido #{pedido.id_pedido} está siendo procesado.')
                else:
                    # Other payments also need approval
                    pedido.estado_pedido_general = 'procesando_pago'
                    messages.success(request, f'Tu pago ha sido registrado. El pedido #{pedido.id_pedido} está siendo procesado.')
                
                pedido.save()
                
                return redirect('pedidos:mis_pedidos')
                
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return render(request, 'usuarios/procesar_pago.html', {'pedido': pedido})
    
    return render(request, 'usuarios/procesar_pago.html', {'pedido': pedido})