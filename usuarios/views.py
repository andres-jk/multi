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
            usuario = form.save()
            # Si el usuario es cliente, crea el objeto Cliente relacionado
            # Asumiendo que el campo 'rol' está en tu modelo Usuario y se establece en el formulario
            if usuario.rol == 'cliente': # Asegúrate de que `usuario.rol` se asigne en tu RegistroForm o en el modelo Usuario por defecto.
                Cliente.objects.create(
                    usuario=usuario,
                    telefono=form.cleaned_data.get('telefono', ''),
                    direccion=form.cleaned_data.get('direccion', '') # Asumiendo que 'direccion' es parte de tu modelo Usuario
                )
            login(request, usuario)
            messages.success(request, '¡Registro exitoso! Bienvenido a MultiAndamios.')
            return redirect('usuarios:inicio_cliente')
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
        tipo_renta = request.POST.get('tipo_renta', 'mensual')
        periodo_renta = int(request.POST.get('periodo_renta', 1))
        
        if tipo_renta not in ['mensual', 'semanal']:
            messages.error(request, 'Tipo de renta inválido. Se estableció a mensual por defecto.')
            tipo_renta = 'mensual'
        
        if cantidad <= 0 or periodo_renta <= 0:
            messages.error(request, 'La cantidad y el período de renta deben ser valores positivos.')
            return redirect('productos:detalle_producto', producto_id=producto_id)

        if producto.cantidad_disponible < cantidad:
            messages.error(request, f'Solo hay {producto.cantidad_disponible} unidades disponibles de {producto.nombre}.')
            return redirect('productos:detalle_producto', producto_id=producto_id)
        
        carrito_item, created = CarritoItem.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={
                'cantidad': cantidad,
                'tipo_renta': tipo_renta,
                'periodo_renta': periodo_renta,
                'meses_renta': periodo_renta # Mantener compatibilidad legacy si es necesario
            }
        )
        
        if not created:
            # Si el item ya existía, actualizar los valores
            # Es importante decidir si se SUMA la cantidad o se REEMPLAZA. Aquí se REEMPLAZA.
            carrito_item.cantidad = cantidad
            carrito_item.tipo_renta = tipo_renta
            carrito_item.periodo_renta = periodo_renta
            carrito_item.meses_renta = periodo_renta # Mantener compatibilidad legacy
            carrito_item.save()
        
        messages.success(request, 'Producto agregado al carrito exitosamente.')
        
    except Producto.DoesNotExist:
        messages.error(request, 'El producto seleccionado no existe.')
    except ValueError:
        messages.error(f'Cantidad o período de renta inválidos. Asegúrate de ingresar números enteros.')
    except Exception as e:
        messages.error(f'Ocurrió un error inesperado al agregar al carrito: {str(e)}')
    
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
        peso_total += item.peso_total # Acumular peso total
        
        # Dibujar fondo de la fila
        p.setFillColor(colors.white)
        p.rect(40, current_y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
        p.setFillColor(colors.black)
        
        # Datos de la fila
        x = 40
        precio_unitario = item.producto.get_precio_por_tipo(item.tipo_renta)
        duracion_texto = item.get_descripcion_periodo()
        
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
    
    direcciones = Direccion.objects.filter(cliente=cliente)
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
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
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
    cliente = get_object_or_404(Cliente, usuario=request.user)
    departamentos = Departamento.objects.all().order_by('nombre')

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = cliente
            direccion.usuario = request.user # Asigna el usuario directamente al modelo Direccion si tiene ese campo
            direccion.save()
            
            # Si esta dirección es marcada como principal, actualizar las demás
            if direccion.es_principal:
                Direccion.objects.filter(cliente=cliente).exclude(id=direccion.id).update(es_principal=False)
            
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
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__usuario=request.user)
    departamentos = Departamento.objects.all().order_by('nombre')
    municipios = Municipio.objects.filter(departamento=direccion.departamento).order_by('nombre')

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            direccion = form.save(commit=False)
            es_principal_nueva = form.cleaned_data.get('es_principal')
            
            # Si se marca como principal y no lo era, o si se desmarca
            if es_principal_nueva and not direccion.es_principal:
                Direccion.objects.filter(cliente=direccion.cliente).update(es_principal=False)
            direccion.es_principal = es_principal_nueva
            
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
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__usuario=request.user)
    
    # No permitir eliminar la única dirección principal
    if direccion.es_principal and Direccion.objects.filter(cliente=direccion.cliente).count() == 1:
        messages.error(request, 'No puedes eliminar tu única dirección principal. Debes tener al menos una dirección principal.')
        return redirect('usuarios:perfil')
    
    with transaction.atomic():
        # Si se elimina la dirección principal, establecer otra como principal
        if direccion.es_principal:
            # Encuentra la primera dirección NO eliminada que no sea la actual
            nueva_principal = Direccion.objects.filter(cliente=direccion.cliente).exclude(id=direccion.id).first()
            if nueva_principal:
                nueva_principal.es_principal = True
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
    total_pedido = subtotal + iva # Este es el total del pedido sin el costo de transporte inicial

    context = {
        'items': carrito_items,
        'departamentos': departamentos,
        'subtotal': subtotal,
        'iva': iva,
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
                # Aquí se está creando una nueva dirección, lo cual es válido si se quiere registrar la dirección exacta de cada pedido.
                # Si prefieres usar una dirección existente del cliente, la lógica debería ser diferente (ej. obtener por id o crear si no existe)
                direccion_envio, created_direccion = Direccion.objects.get_or_create(
                    cliente=get_object_or_404(Cliente, usuario=request.user), # Asegurarse de que el cliente exista
                    calle=calle,
                    numero=numero,
                    complemento=complemento,
                    departamento=departamento,
                    municipio=municipio,
                    codigo_divipola=codigo_divipola,
                    codigo_postal=codigo_postal,
                    defaults={'es_principal': False} # Por defecto no es principal si se crea aquí
                )
                
                # 3. Crear el Pedido
                pedido = Pedido.objects.create(
                    cliente=get_object_or_404(Cliente, usuario=request.user),
                    fecha=timezone.now(),
                    total=total_pedido, # Total sin costo de transporte aún
                    estado='pendiente', # O 'procesando', 'confirmado'
                    notas=notas,
                    direccion_envio=direccion_envio # Asignar la dirección al pedido
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
                        precio_unitario=item.producto.get_precio_por_tipo(item.tipo_renta),
                        tipo_renta=item.tipo_renta,
                        periodo_renta=item.periodo_renta,
                        subtotal=item.subtotal
                    )
                    # Marcar el item del carrito como 'reservado' o 'procesado' si no se elimina inmediatamente
                    # Si los items se eliminan del carrito, no es necesario marcarlos como reservados aquí.
                    # Asumo que 'reservado' es para la remisión, pero en un checkout exitoso se borrarían.
                    item.delete() # Eliminar el item del carrito después de procesarlo
                
                messages.success(request, f'Tu pedido #{pedido.id_pedido} ha sido realizado exitosamente.')
                return redirect('usuarios:perfil') # O a una página de confirmación de pedido

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