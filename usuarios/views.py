from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django import forms
from django.utils import timezone
from pedidos.models import Pedido, DetallePedido
from productos.models import Producto
from recibos.models import ReciboObra
from .forms import UsuarioForm, ClienteForm, DireccionForm, MetodoPagoForm
from .models import Usuario, Cliente, MetodoPago, Direccion, CarritoItem
from .models_divipola import Departamento, Municipio

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os
from reportlab.lib import colors
from reportlab.lib.units import mm, inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer

from datetime import datetime, timedelta
import os
import uuid
import io

def inicio_cliente(request):
    """Vista para la página de inicio de clientes"""
    productos_destacados = Producto.objects.filter(cantidad_disponible__gt=0).order_by('-id_producto')[:6]
    return render(request, 'usuarios/inicio_cliente.html', {
        'productos_destacados': productos_destacados
    })

class RegistroForm(UserCreationForm):
    numero_identidad = forms.CharField(label='Número de Identidad', max_length=20)
    first_name = forms.CharField(label='Nombre', max_length=30)
    last_name = forms.CharField(label='Apellido', max_length=30)
    email = forms.EmailField(label='Correo')
    direccion = forms.CharField(label='Dirección', max_length=255)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)

    class Meta:
        model = Usuario
        fields = ('numero_identidad', 'username', 'first_name', 'last_name', 'email', 'direccion', 'telefono', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.numero_identidad = self.cleaned_data['numero_identidad']
        if commit:
            user.save()
        return user

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Si el usuario es cliente, crea el objeto Cliente relacionado
            if usuario.rol == 'cliente':
                Cliente.objects.create(
                    usuario=usuario,
                    telefono=form.cleaned_data.get('telefono', ''),
                    direccion=form.cleaned_data.get('direccion', '')
                )
            login(request, usuario)
            return redirect('usuarios:inicio_cliente')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def inicio(request):
    return render(request, 'usuarios/inicio.html')

def productos(request):
    productos = Producto.objects.all()
    return render(request, 'usuarios/productos.html', {'productos': productos})

@login_required
def agregar_al_carrito(request, producto_id):
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('productos:detalle_producto', producto_id=producto_id)
    
    try:
        producto = Producto.objects.get(id_producto=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        meses_renta = int(request.POST.get('meses_renta', 1))
        
        # Validar la cantidad disponible
        if producto.cantidad_disponible < cantidad:
            messages.error(request, f'Solo hay {producto.cantidad_disponible} unidades disponibles.')
            return redirect('productos:detalle_producto', producto_id=producto_id)
        
        # Obtener o crear el item en el carrito
        carrito_item, created = CarritoItem.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={
                'cantidad': cantidad,
                'meses_renta': meses_renta
            }
        )
        
        if not created:
            # Si el item ya existía, actualizar la cantidad
            carrito_item.cantidad = cantidad
            carrito_item.meses_renta = meses_renta
            carrito_item.save()
        
        messages.success(request, 'Producto agregado al carrito exitosamente.')
        
    except Producto.DoesNotExist:
        messages.error(request, 'El producto no existe.')
    except ValueError:
        messages.error(request, 'Cantidad o meses de renta inválidos.')
    except Exception as e:
        messages.error(request, f'Error al agregar al carrito: {str(e)}')
    
    return redirect('usuarios:ver_carrito')

@login_required
def ver_carrito(request):
    """Vista para ver el contenido del carrito"""
    # Obtener los items del carrito del usuario actual
    items_carrito = CarritoItem.objects.filter(usuario=request.user)
    
    # Calcular el total sumando los subtotales
    total = sum(item.subtotal for item in items_carrito)
    
    context = {
        'items_carrito': items_carrito,
        'total': total,
    }
    
    return render(request, 'usuarios/carrito.html', context)

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    
    if item.reservado:
        # Devolver productos al inventario si están reservados
        producto = item.producto
        producto.cantidad_disponible += item.cantidad
        producto.save()
    
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('usuarios:ver_carrito')

@login_required
def limpiar_carrito(request):
    """Vista para limpiar todos los items del carrito"""
    items = CarritoItem.objects.filter(usuario=request.user)
    
    for item in items:
        if item.reservado:
            item.liberar_reserva()
        item.delete()
    
    messages.success(request, "Se ha limpiado el carrito exitosamente.")
    return redirect('usuarios:ver_carrito')

def iniciar_sesion(request):
    mensaje = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('usuarios:inicio_cliente')
        else:
            mensaje = 'Usuario o contraseña incorrectos.'
    return render(request, 'usuarios/login.html', {'mensaje': mensaje})

def cerrar_sesion(request):
    """
    Cierra la sesión del usuario y redirecciona a la página de inicio.
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('usuarios:inicio_cliente')

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuarios:login')

def draw_emisor_receptor_box(p, emisor, receptor, x, y, width):
    box_height = 70
    col_sep = x + width // 2
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.roundRect(x, y - box_height, width, box_height, 8, stroke=1, fill=0)
    # Emisor
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x + 10, y - 15, "Emisor:")
    p.setFont("Helvetica", 9)
    p.drawString(x + 10, y - 30, f"{emisor['nombre']}")
    p.drawString(x + 10, y - 42, f"NIT: {emisor['nif']}")
    p.drawString(x + 10, y - 54, f"Dirección: {emisor['direccion']}")
    p.drawString(x + 10, y - 66, f"Tel: {emisor['telefono']}")
    # Receptor
    p.setFont("Helvetica-Bold", 10)
    p.drawString(col_sep + 10, y - 15, "Receptor:")
    p.setFont("Helvetica", 9)
    p.drawString(col_sep + 10, y - 30, f"{receptor['nombre']}")
    p.drawString(col_sep + 10, y - 42, f"NIF/CIF: {receptor['nif']}")
    p.drawString(col_sep + 10, y - 54, f"Dirección: {receptor['direccion']}")

def draw_table_header(p, headers, x, y, col_widths, height=18):
    p.setFillColor(colors.HexColor("#FFD600"))
    p.rect(x, y - height, sum(col_widths), height, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)
    x0 = x
    for i, h in enumerate(headers):
        p.drawString(x0 + 4, y - height + 5, h)
        x0 += col_widths[i]

def draw_table_row(p, row, x, y, col_widths, height=16):
    p.setFillColor(colors.white)
    p.rect(x, y - height, sum(col_widths), height, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    x0 = x
    for i, cell in enumerate(row):
        p.drawString(x0 + 4, y - height + 4, str(cell))
        x0 += col_widths[i]

@login_required
def generar_cotizacion_pdf(request):
    try:
        # Obtener items del carrito del modelo CarritoItem
        items_carrito = CarritoItem.objects.filter(usuario=request.user)
        
        if not items_carrito.exists():
            messages.error(request, 'El carrito está vacío')
            return redirect('usuarios:ver_carrito')

        # Crear el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
        
        # Inicializar el PDF
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        def draw_page_header():
            # Encabezado con fondo amarillo
            p.setFillColor(colors.HexColor("#FFD600"))
            p.rect(0, height - 60, width, 60, fill=1, stroke=0)
            
            # Logo o Título
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 22)
            p.drawCentredString(width/2, height - 40, "COTIZACIÓN")
            
            # Información de la empresa
            p.setFont("Helvetica", 10)
            p.drawRightString(width - 50, height - 55, "MULTIANDAMIOS S.A.S.")
    
        # Primera página
        draw_page_header()
        y = height - 80

        # Marco para información
        p.setLineWidth(0.5)
        p.rect(40, y - 160, width - 80, 140, stroke=1, fill=0)
    
        # Información de la empresa y cliente    
        emisor = {
            'nombre': 'MULTIANDAMIOS S.A.S.',
            'nif': 'NIT 900.252.510-1',
            'direccion': 'Cra. 128 #22A-45, Bogotá, Colombia',
            'telefono': '+57 310 574 2020',
            'email': 'info@multiandamios.co'
        }
    
        user = request.user
        receptor = {
            'nombre': f"{user.first_name} {user.last_name}".strip() or "N/A",
            'nif': str(getattr(user, 'numero_identidad', 'N/A')),
            'direccion': str(getattr(user, 'direccion', 'N/A')),
            'telefono': str(getattr(user, 'telefono', 'N/A')),
            'email': str(user.email or 'N/A')
        }
    
        # Títulos de secciones
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y - 15, "DATOS DEL PROVEEDOR")
        p.drawString(width/2 + 10, y - 15, "DATOS DEL CLIENTE")
    
        # Información del emisor
        y -= 35
        p.setFont("Helvetica", 10)
        for key, value in emisor.items():
            label = key.upper() + ": "
            p.setFont("Helvetica-Bold", 9)
            p.drawString(50, y, label)
            p.setFont("Helvetica", 9)
            p.drawString(50 + p.stringWidth(label, "Helvetica-Bold", 9), y, value)
            y -= 15
    
        # Información del receptor
        y = height - 115
        for key, value in receptor.items():
            label = key.upper() + ": "
            p.setFont("Helvetica-Bold", 9)
            p.drawString(width/2 + 10, y, label)
            p.setFont("Helvetica", 9)
            str_value = str(value) if value is not None else "N/A"
            p.drawString(width/2 + 10 + p.stringWidth(label, "Helvetica-Bold", 9), y, str_value)
            y -= 15
    
        # Información de la cotización
        y = height - 200
        p.setFont("Helvetica", 10)
        fecha = datetime.now()
        p.drawString(50, y, f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}")
        p.drawString(width - 200, y, f"Cotización #: {uuid.uuid4().hex[:8].upper()}")
    
        # Tabla de productos
        y -= 40
        headers = ["Descripción", "Cant.", "Meses", "Precio Unit.", "Subtotal"]
        col_widths = [250, 60, 60, 80, 80]
        row_height = 20

        def draw_table_header(y_pos):
            # Fondo del encabezado
            p.setFillColor(colors.HexColor("#F5F5F5"))
            p.rect(40, y_pos - row_height, sum(col_widths), row_height, fill=1, stroke=1)
            
            # Textos del encabezado
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 10)
            x = 40
            for i, header in enumerate(headers):
                p.drawString(x + 5, y_pos - 15, header)
                x += col_widths[i]
            return y_pos - row_height

        # Dibujar encabezado inicial
        y = draw_table_header(y)
        
        # Contenido de la tabla
        p.setFont("Helvetica", 9)
        total_sin_iva = 0

        for item in items_carrito:
            if y < 100:  # Nueva página si no hay espacio
                p.showPage()
                draw_page_header()
                y = height - 100
                y = draw_table_header(y)
                p.setFont("Helvetica", 9)

            # Calcular subtotal
            subtotal = item.producto.precio * item.cantidad * item.meses_renta
            total_sin_iva += subtotal
            
            # Dibujar fondo de la fila
            p.setFillColor(colors.white)
            p.rect(40, y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
            p.setFillColor(colors.black)
            
            # Datos de la fila
            x = 40
            row_data = [
                item.producto.nombre[:40],
                str(item.cantidad),
                str(item.meses_renta),
                f"${item.producto.precio:,.2f}",
                f"${subtotal:,.2f}"
            ]
            
            for i, text in enumerate(row_data):
                p.drawString(x + 5, y - 15, text)
                x += col_widths[i]
            
            y -= row_height

        # Totales
        y -= 20
        p.setFont("Helvetica-Bold", 10)
        iva = total_sin_iva * Decimal('0.19')  # 19% IVA
        total_con_iva = total_sin_iva + iva

        # Dibujar recuadro para totales
        p.setFillColor(colors.HexColor("#F5F5F5"))
        totals_x = width - 250
        p.rect(totals_x, y - 60, 200, 60, fill=1, stroke=1)
        p.setFillColor(colors.black)

        # Mostrar totales
        p.drawString(totals_x + 10, y - 20, f"Subtotal: ${total_sin_iva:,.2f}")
        p.drawString(totals_x + 10, y - 40, f"IVA (19%): ${iva:,.2f}")
        p.setFillColor(colors.HexColor("#FFD600"))
        p.rect(totals_x, y - 60, 200, 20, fill=1, stroke=1)
        p.setFillColor(colors.black)
        p.drawString(totals_x + 10, y - 55, f"Total: ${total_con_iva:,.2f}")

        # Observaciones
        y -= 90
        p.setFont("Helvetica", 9)
        p.drawString(40, y, "OBSERVACIONES:")
        y -= 15
        p.drawString(40, y, "• Esta cotización tiene validez de 15 días.")
        y -= 15
        p.drawString(40, y, "• Los precios incluyen IVA del 19%.")
        y -= 15
        p.drawString(40, y, "• El costo del transporte no está incluido y depende de la zona de entrega.")
        y -= 15
        p.drawString(40, y, "• Forma de pago: Contra entrega o transferencia bancaria.")

        # Firmas
        y -= 40
        p.line(50, y, 250, y)
        p.line(width-250, y, width-50, y)
        p.setFont("Helvetica", 10)
        p.drawCentredString(150, y-20, "Firma del Cliente")
        p.drawCentredString(width-150, y-20, "Firma del Proveedor")

        # Pie de página
        p.setFont("Helvetica", 8)
        p.drawString(40, 30, "MULTIANDAMIOS S.A.S. - Servicio al cliente: +57 310 574 2020")
        p.drawString(40, 20, "Email: info@multiandamios.co | www.multiandamios.co")
    
        p.save()
        return response

    except Exception as e:
        messages.error(request, f'Error al generar la cotización: {str(e)}')
        return redirect('usuarios:ver_carrito')

@login_required
def generar_remision_pdf(request):
    carrito = CarritoItem.objects.filter(usuario=request.user, reservado=True).select_related('producto')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="remision.pdf"'
    
    # Inicializar el PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Encabezado con fondo amarillo
    p.setFillColor(colors.HexColor("#FFD600"))
    p.rect(0, height - 60, width, 60, fill=1, stroke=0)
    
    # Logo o Título
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(width/2, height - 40, "REMISIÓN")
    
    # Información de la empresa
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 50, height - 55, "MULTIANDAMIOS S.A.S.")
    
    y = height - 80
    
    # Marco para información
    p.setLineWidth(0.5)
    p.rect(40, y - 160, width - 80, 140, stroke=1, fill=0)
    
    # Información de la empresa y cliente    
    emisor = {
        'nombre': 'MULTIANDAMIOS S.A.S.',
        'nif': 'NIT 900.252.510-1',
        'direccion': 'Cra. 128 #22A-45, Bogotá, Colombia',
        'telefono': '+57 310 574 2020',
        'email': 'info@multiandamios.co'
    }
    
    user = request.user
    receptor = {
        'nombre': f"{user.first_name} {user.last_name}".strip() or "N/A",
        'nif': str(getattr(user, 'numero_identidad', 'N/A')),
        'direccion': str(getattr(user, 'direccion', 'N/A')),
        'telefono': str(getattr(user, 'telefono', 'N/A')),
        'email': str(user.email or 'N/A')
    }
    
    # Dividir el espacio en dos columnas
    col_width = (width - 100) / 2
    
    # Títulos de secciones
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y - 15, "DATOS DEL PROVEEDOR")
    p.drawString(width/2 + 10, y - 15, "DATOS DEL CLIENTE")
    
    # Información del emisor
    y -= 35
    p.setFont("Helvetica", 10)
    for key, value in emisor.items():
        label = key.upper() + ": "
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, y, label)
        p.setFont("Helvetica", 9)
        p.drawString(50 + p.stringWidth(label, "Helvetica-Bold", 9), y, value)
        y -= 15
    
    # Información del receptor
    y = height - 115
    for key, value in receptor.items():
        label = key.upper() + ": "
        p.setFont("Helvetica-Bold", 9)
        p.drawString(width/2 + 10, y, label)
        p.setFont("Helvetica", 9)
        str_value = str(value) if value is not None else "N/A"
        p.drawString(width/2 + 10 + p.stringWidth(label, "Helvetica-Bold", 9), y, str_value)
        y -= 15
    
    # Información de la remisión
    y = height - 200
    p.setFont("Helvetica", 10)
    fecha = datetime.now()
    p.drawString(50, y, f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(width - 200, y, f"Remisión #: {uuid.uuid4().hex[:8].upper()}")
    
    # Tabla de productos
    y -= 40
    headers = ["Descripción", "Cant.", "Meses", "Precio Unit.", "Subtotal"]
    col_widths = [250, 60, 60, 80, 80]
    row_height = 20
    
    # Fondo del encabezado
    p.setFillColor(colors.HexColor("#F5F5F5"))
    p.rect(40, y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
    
    # Textos del encabezado
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    x = 40
    for i, header in enumerate(headers):
        p.drawString(x + 5, y - 15, header)
        x += col_widths[i]
    
    # Contenido de la tabla
    y -= row_height
    p.setFont("Helvetica", 9)
    total = 0
    
    for item in carrito:
        if y < 180:  # Nueva página si no hay espacio
            p.showPage()
            y = height - 100
            p.setFont("Helvetica", 9)
        
        subtotal = item.producto.precio * item.cantidad * item.meses_renta
        total += subtotal
        
        # Dibujar fila
        p.setFillColor(colors.white)
        p.rect(40, y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
        p.setFillColor(colors.black)
        
        x = 40
        row_data = [
            item.producto.nombre[:40],
            str(item.cantidad),
            str(item.meses_renta),
            f"${item.producto.precio:,.2f}",
            f"${subtotal:,.2f}"
        ]
        
        for i, text in enumerate(row_data):
            p.drawString(x + 5, y - 15, text)
            x += col_widths[i]
        
        y -= row_height
    
    # Total
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width - 200, y, f"Total: ${total:,.2f}")
    
    # Firmas
    y -= 60
    p.line(50, y, 250, y)
    p.line(width-250, y, width-50, y)
    p.setFont("Helvetica", 10)
    p.drawCentredString(150, y-20, "Firma del Cliente")
    p.drawCentredString(width-150, y-20, "Firma del Proveedor")
    
    p.showPage()
    p.save()
    return response

@login_required
def perfil(request):
    """Vista para mostrar el perfil del usuario"""
    # Obtener o crear el cliente asociado al usuario
    cliente, created = Cliente.objects.get_or_create(
        usuario=request.user,
        defaults={
            'telefono': '',
            'direccion': request.user.direccion or ''
        }
    )
    
    # Obtener las direcciones del cliente
    direcciones = Direccion.objects.filter(cliente=cliente)
      # Obtener los pedidos del cliente
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
    if request.method == 'POST':
        # Actualizar información del usuario
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.direccion = request.POST.get('direccion')
        request.user.save()
        
        # Actualizar o crear información del cliente
        cliente, created = Cliente.objects.get_or_create(usuario=request.user)
        cliente.telefono = request.POST.get('telefono')
        cliente.direccion = request.POST.get('direccion')
        cliente.save()
        
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('usuarios:perfil')
        
    # Si es GET, mostrar el formulario con la información actual
    cliente = Cliente.objects.filter(usuario=request.user).first()
    context = {
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
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores indicados.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'usuarios/cambiar_contrasena.html', {
        'form': form
    })

@login_required
def agregar_direccion(request):
    """Vista para agregar una nueva dirección"""
    if request.method == 'POST':
        # Obtener el cliente asociado al usuario
        cliente = get_object_or_404(Cliente, usuario=request.user)
        
        # Crear la nueva dirección
        direccion = Direccion.objects.create(
            cliente=cliente,
            calle=request.POST.get('calle'),
            ciudad=request.POST.get('ciudad'),
            departamento=request.POST.get('departamento'),
            codigo_postal=request.POST.get('codigo_postal'),
            es_principal=request.POST.get('es_principal', False) == 'on'
        )
        
        # Si esta dirección es marcada como principal, actualizar las demás
        if direccion.es_principal:
            Direccion.objects.filter(cliente=cliente).exclude(id=direccion.id).update(es_principal=False)
        
        messages.success(request, 'Dirección agregada exitosamente.')
        return redirect('usuarios:perfil')
    
    return render(request, 'usuarios/agregar_direccion.html')

@login_required
def editar_direccion(request, direccion_id):
    """Vista para editar una dirección existente"""
    # Obtener la dirección asegurando que pertenezca al cliente actual
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__usuario=request.user)
    
    if request.method == 'POST':
        # Actualizar los campos de la dirección
        direccion.calle = request.POST.get('calle')
        direccion.ciudad = request.POST.get('ciudad')
        direccion.departamento = request.POST.get('departamento')
        direccion.codigo_postal = request.POST.get('codigo_postal')
        es_principal = request.POST.get('es_principal', False) == 'on'
        
        # Si se marca como principal, actualizar las demás direcciones
        if es_principal and not direccion.es_principal:
            Direccion.objects.filter(cliente=direccion.cliente).update(es_principal=False)
            direccion.es_principal = True
        
        direccion.save()
        messages.success(request, 'Dirección actualizada exitosamente.')
        return redirect('usuarios:perfil')
    
    return render(request, 'usuarios/editar_direccion.html', {'direccion': direccion})

@login_required
def eliminar_direccion(request, direccion_id):
    """Vista para eliminar una dirección"""
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__usuario=request.user)
    
    # No permitir eliminar la única dirección principal
    if direccion.es_principal and not Direccion.objects.filter(cliente=direccion.cliente).exclude(id=direccion_id).exists():
        messages.error(request, 'No puedes eliminar tu única dirección principal.')
        return redirect('usuarios:perfil')
    
    # Si se elimina la dirección principal, establecer otra como principal
    if direccion.es_principal:
        nueva_principal = Direccion.objects.filter(cliente=direccion.cliente).exclude(id=direccion_id).first()
        if nueva_principal:
            nueva_principal.es_principal = True
            nueva_principal.save()
    
    direccion.delete()
    messages.success(request, 'Dirección eliminada exitosamente.')
    return redirect('usuarios:perfil')

@login_required
def checkout(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    if not carrito_items.exists():
        messages.error(request, 'Tu carrito está vacío')
        return redirect('usuarios:ver_carrito')
    
    departamentos = Departamento.objects.all().order_by('nombre')

    # Prepare context for GET request and POST error cases
    subtotal = sum(item.subtotal for item in carrito_items)
    iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = subtotal + iva
    
    context = {
        'items': carrito_items,
        'departamentos': departamentos,
        'subtotal': subtotal,
        'iva': iva,
        'total': total, # This is total before transport cost
    }

    if request.method == 'POST':
        departamento_id = request.POST.get('departamento')
        municipio_id = request.POST.get('municipio')
        codigo_divipola = request.POST.get('codigo_divipola')
        codigo_postal = request.POST.get('codigo_postal')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento', '')
        notas = request.POST.get('notas', '')

        if not all([departamento_id, municipio_id, codigo_divipola, calle, numero]):
            messages.error(request, 'Por favor complete todos los campos obligatorios de la dirección.')
            return render(request, 'usuarios/checkout.html', context)

        try:
            with transaction.atomic():
                # Marcar items como en proceso de pago
                for item in carrito_items:
                    item.en_proceso_pago = True
                    item.save()

                # Construir la dirección completa
                departamento = Departamento.objects.get(id=departamento_id)
                municipio = Municipio.objects.get(id=municipio_id)
                direccion_completa = f"{calle} {numero} {complemento}, {municipio.nombre}, {departamento.nombre}"

                # Crear o actualizar la dirección con información DIVIPOLA
                Direccion.objects.create(
                    usuario=request.user,
                    departamento_id=departamento_id,
                    municipio_id=municipio_id,
                    codigo_divipola=codigo_divipola,
                    codigo_postal=codigo_postal,
                    calle=calle,
                    numero=numero,
                    complemento=complemento
                )

                # Calcular el total del pedido
                subtotal_pedido = sum(item.subtotal for item in carrito_items)
                costo_transporte = municipio.costo_transporte if municipio.costo_transporte else Decimal('0')


                # Crear el pedido
                pedido = Pedido.objects.create(
                    cliente=request.user.cliente,
                    estado_pedido_general='pendiente_pago',
                    direccion_entrega=direccion_completa,
                    subtotal=subtotal_pedido,
                    costo_transporte=costo_transporte,
                    notas=notas,
                    duracion_renta=max(item.meses_renta for item in carrito_items),
                    fecha_limite_pago=timezone.now() + timedelta(hours=24)
                )

                # Crear detalles del pedido
                for item in carrito_items:
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.precio,
                        subtotal=item.subtotal,
                        meses_renta=item.meses_renta
                    )
                    
                    # Reservar el producto
                    item.reservar()

                # Limpiar el carrito
                carrito_items.delete()

                messages.success(request, 'Pedido creado exitosamente. Tienes 24 horas para realizar el pago.')
                return redirect('usuarios:pago_recibo', pedido_id=pedido.id_pedido)
            
        except Exception as e:
            # En caso de error, desmarcar los items como en proceso
            for item in carrito_items:
                item.en_proceso_pago = False
                item.save()
            
            messages.error(request, f'Error al procesar el pedido: {str(e)}')
            return render(request, 'usuarios/checkout.html', context)

    # GET request - show the checkout form
    return render(request, 'usuarios/checkout.html', context)

@login_required
def mis_pedidos(request):
    # Obtenemos el cliente asociado al usuario actual
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    # Obtenemos todos los pedidos del cliente ordenados por fecha descendente
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    
    # Procesar pedidos pendientes de pago
    for pedido in pedidos:
        if pedido.estado_pedido_general == 'pendiente_pago':
            # Verificar si el pago está vencido
            if pedido.esta_vencido_pago():
                pedido.estado_pedido_general = 'pago_vencido'
                pedido.save()
            else:
                # Calcular tiempo restante para pedidos pendientes
                tiempo_restante = pedido.get_tiempo_restante_pago()
                if tiempo_restante:
                    horas = int(tiempo_restante.total_seconds() / 3600)
                    minutos = int((tiempo_restante.total_seconds() % 3600) / 60)
                    pedido.tiempo_restante_str = f"{horas}h {minutos}m"
    
    # Contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'cliente': cliente,
    }
    
    return render(request, 'usuarios/mis_pedidos.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    """Vista para mostrar el detalle de un pedido específico"""
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente__usuario=request.user)
    detalles = DetallePedido.objects.filter(pedido=pedido).select_related('producto')
    
    return render(request, 'usuarios/detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles,
        'total': pedido.total
    })

@login_required
def generar_recibo_pdf(request, pedido_id):
    # Obtener el pedido y verificar que pertenece al usuario actual
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente__usuario=request.user)
    
    # Crear el buffer para el PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Configuración inicial
    styles = getSampleStyleSheet()
    p.setFont("Helvetica-Bold", 16)
    
    # Encabezado
    p.drawString(50, height - 50, "MultiAndamios")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Recibo de Pedido #{pedido.id_pedido}")
    p.drawString(50, height - 90, f"Fecha: {pedido.fecha.strftime('%d/%m/%Y %H:%M')}")
    
    # Información del cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 120, "Información del Cliente:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 140, f"Cliente: {pedido.cliente.usuario.get_full_name()}")
    p.drawString(50, height - 160, f"Dirección de entrega: {pedido.direccion_entrega}")
    
    # Detalles del pedido
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 190, "Detalles del Pedido:")
    
    # Tabla de productos
    data = [['Producto', 'Cantidad', 'Precio Unitario', 'Total']]
    detalles = DetallePedido.objects.filter(pedido=pedido)
    
    y_position = height - 220
    
    for detalle in detalles:
        data.append([
            detalle.producto.nombre,
            str(detalle.cantidad),
            f"${detalle.precio_unitario:,.2f}",
            f"${detalle.subtotal:,.2f}"
        ])
    
    table = Table(data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - len(data) * 20)
    
    # Total
    total_y = y_position - (len(data) * 20) - 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, total_y, f"Total: ${pedido.total:,.2f}")
    
    # Estado del pedido
    p.setFont("Helvetica", 12)
    p.drawString(50, total_y - 30, f"Estado del pedido: {pedido.get_estado_pedido_general_display()}")
    
    # Notas
    if pedido.notas:
        p.drawString(50, total_y - 50, f"Notas: {pedido.notas}")
    
    # Pie de página
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, "Este documento es un recibo digital generado automáticamente.")
    p.drawString(50, 35, f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Guardar PDF
    p.showPage()
    p.save()
    
    # Preparar la respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_pedido_{pedido.id_pedido}.pdf"'
    
    return response

@login_required
def pago_recibo(request, pedido_id):
    """Vista para procesar el pago de un pedido"""
    # Verificar que el usuario sea cliente
    if not request.user.rol == 'cliente':
        messages.error(request, 'Solo los clientes pueden realizar pagos.')
        return redirect('usuarios:inicio_cliente')
    
    try:
        # Obtener el pedido verificando que pertenezca al usuario
        pedido = get_object_or_404(Pedido, 
                                 id_pedido=pedido_id, 
                                 cliente__usuario=request.user)
        
        # Validaciones iniciales
        if pedido.estado_pedido_general == 'pagado':
            messages.info(request, "Este pedido ya ha sido pagado.")
            return redirect('usuarios:confirmacion_pago', pedido_id=pedido.id_pedido)
        
        if pedido.estado_pedido_general == 'procesando_pago':
            messages.info(request, "Este pedido está en proceso de verificación de pago.")
            return redirect('usuarios:confirmacion_pago', pedido_id=pedido.id_pedido)
        
        if pedido.esta_vencido_pago():
            pedido.estado_pedido_general = 'pago_vencido'
            pedido.save()
            messages.error(request, "El tiempo para realizar el pago ha expirado.")
            return redirect('usuarios:mis_pedidos')
        
        # Procesar el formulario de pago
        if request.method == 'POST':
            form = MetodoPagoForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Crear la instancia de MetodoPago
                        pago = form.save(commit=False)
                        pago.usuario = request.user
                        pago.pedido = pedido
                        pago.monto = pedido.total
                        pago.estado = 'pendiente'
                        pago.save()

                        # Actualizar el estado del pedido a 'procesando_pago'
                        pedido.estado_pedido_general = 'procesando_pago'
                        pedido.metodo_pago = pago.tipo
                        pedido.save()
                        
                        messages.info(request, "Tu comprobante de pago ha sido recibido y está pendiente de verificación.")
                        return redirect('usuarios:confirmacion_pago', pedido_id=pedido.id_pedido)

                except ValidationError as e:
                    messages.error(request, str(e))
                except Exception as e:
                    messages.error(request, f"Error inesperado al procesar el pago: {str(e)}")
                
                # Si hay un error, redirigir de vuelta al formulario de pago
                return redirect('usuarios:pago_recibo', pedido_id=pedido.id_pedido)
        else:
            form = MetodoPagoForm()

        # Contexto para la plantilla
        try:
            context = {
                'pedido': pedido,
                'detalles': pedido.detalles.all().select_related('producto'),
                'pago_form': form,
                'tiempo_restante': pedido.get_tiempo_restante_pago(),
                'datos_bancarios': {
                    'banco': 'Bancolombia',
                    'tipo_cuenta': 'Cuenta de Ahorros',
                    'numero_cuenta': '123456789',
                    'titular': 'MultiAndamios S.A.S',
                    'nit': '900.123.456-7'
                },
                'subtotal': pedido.subtotal,
                'iva': pedido.iva,
                'costo_transporte': pedido.costo_transporte,
                'total_con_iva': pedido.total
            }
        
            return render(request, 'usuarios/pago.html', context)
        
        except Exception as e:
            messages.error(request, f"Error al cargar los datos del pedido: {str(e)}")
            return redirect('usuarios:mis_pedidos')
        
    except Exception as e:
        messages.error(request, f"Error al cargar la página de pago: {str(e)}")
        return redirect('usuarios:mis_pedidos')

@login_required
def confirmacion_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente__usuario=request.user)
    
    # Obtener los detalles del pedido para mostrarlos en la confirmación
    detalles = pedido.detalles.all().select_related('producto')
    
    # Si está pagado o en verificación, mostrar mensaje apropiado
    if pedido.estado_pedido_general == 'pagado':
        messages.success(request, 'El pago de tu pedido ha sido confirmado.')
    elif pedido.estado_pedido_general == 'pendiente_verificacion':
        messages.info(request, 'Tu pago está siendo verificado por nuestro equipo. Te notificaremos cuando se confirme.')
    else:
        messages.warning(request, 'Tu pedido está pendiente de pago.')
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'subtotal': pedido.subtotal,
        'iva': pedido.iva,
        'costo_transporte': pedido.costo_transporte,
        'total': pedido.total,
    }
    
    return render(request, 'usuarios/confirmacion_pago.html', context)

@login_required
def ver_remision(request, pedido_id):
    # Obtener el pedido y verificar que pertenece al usuario actual
    pedido = get_object_or_404(Pedido, 
                              id_pedido=pedido_id,
                              cliente__usuario=request.user)
    
    # Obtener los detalles del pedido
    detalles = DetallePedido.objects.filter(pedido=pedido)
    
    # Verificar si el pedido está en un estado que permita ver la remisión
    estados_permitidos = ['confirmado', 'en_preparacion', 'listo_entrega', 
                         'parcialmente_entregado', 'totalmente_entregado']
    
    if pedido.estado_pedido_general not in estados_permitidos:
        messages.error(request, 
                      "No se puede generar la remisión para este pedido en su estado actual.")
        return redirect('usuarios:detalle_pedido', pedido_id=pedido_id)
    
    # Preparar el contexto
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'cliente': pedido.cliente,
        'fecha_actual': timezone.now(),
        'total': pedido.total
    }
    
    return render(request, 'usuarios/ver_remision.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def generar_remision_admin(request, pedido_id):
    # Obtener el pedido (sin filtrar por cliente ya que es vista de admin)
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        # Actualizar estado del pedido si se solicita
        nuevo_estado = request.POST.get('estado_pedido')
        if nuevo_estado and nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado_pedido_general = nuevo_estado
            pedido.save()
            messages.success(request, f"Estado del pedido actualizado a: {pedido.get_estado_pedido_general_display()}")
        
        # Generar PDF de remisión
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Configuración inicial
        styles = getSampleStyleSheet()
        p.setFont("Helvetica-Bold", 16)
        
        # Logo y encabezado
        p.drawString(50, height - 50, "MultiAndamios")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, f"Remisión de Entrega - Pedido #{pedido.id_pedido}")
        p.drawString(50, height - 90, f"Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Información de la empresa
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 120, "Información de la Empresa:")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 140, "MultiAndamios")
        p.drawString(50, height - 160, "NIT: 900.123.456-7")
        p.drawString(50, height - 180, "Tel: (123) 456-7890")
        
        # Información del cliente
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 210, "Información del Cliente:")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 230, f"Cliente: {pedido.cliente.usuario.get_full_name()}")
        p.drawString(50, height - 250, f"Documento: {pedido.cliente.tipo_documento} {pedido.cliente.numero_documento}")
        p.drawString(50, height - 270, f"Dirección: {pedido.direccion_entrega}")
        
        # Detalles del pedido
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, height - 310, "Detalles del Pedido:")
        
        # Tabla de productos
        data = [['Producto', 'Cantidad', 'Estado']]
        detalles = DetallePedido.objects.filter(pedido=pedido)
        
        y_position = height - 340
        
        for detalle in detalles:
            data.append([
                detalle.producto.nombre,
                str(detalle.cantidad),
                pedido.get_estado_pedido_general_display()
            ])
        
        table = Table(data, colWidths=[250, 100, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        table.wrapOn(p, width, height)
        table.drawOn(p, 50, y_position - (len(data) * 20))
        
        # Firmas
        y_firma = y_position - (len(data) * 20) - 100
        p.drawString(50, y_firma, "_____________________")
        p.drawString(300, y_firma, "_____________________")
        p.drawString(50, y_firma - 20, "Firma Entrega")
        p.drawString(300, y_firma - 20, "Firma Recibido")
        
        # Notas y condiciones
        if pedido.notas:
            p.drawString(50, y_firma - 60, f"Notas: {pedido.notas}")
        
        # Pie de página
        p.setFont("Helvetica", 8)
        p.drawString(50, 50, "Este documento es una remisión oficial de MultiAndamios")
        p.drawString(50, 35, f"Generado por: {request.user.get_full_name()} - {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Guardar PDF
        p.showPage()
        p.save()
        
        # Preparar la respuesta
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="remision_pedido_{pedido.id_pedido}.pdf"'
        
        return response
    
    # Si es GET, mostrar formulario
    context = {
        'pedido': pedido,
        'detalles': DetallePedido.objects.filter(pedido=pedido),
        'estados': Pedido.ESTADO_CHOICES,
    }
    
    return render(request, 'usuarios/generar_remision_admin.html', context)

@login_required
def actualizar_carrito(request):
    """Vista para actualizar cantidades en el carrito"""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para actualizar el carrito.")
            return redirect('usuarios:login')
        
        for key, value in request.POST.items():
            if key.startswith(('cantidad_', 'meses_')):
                try:
                    item_id = int(key.split('_')[1])
                    nuevo_valor = int(value)
                    if nuevo_valor < 1:
                        continue
                        
                    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
                    
                    if key.startswith('cantidad_'):
                        if nuevo_valor > item.producto.cantidad_disponible:
                            messages.error(request, 
                                         f'No hay suficiente stock de {item.producto.nombre}. '
                                         f'Solo hay {item.producto.cantidad_disponible} disponibles.')
                            continue
                        item.cantidad = nuevo_valor
                    else:  # meses_
                        if nuevo_valor > 12:
                            messages.error(request, 
                                         f'El período máximo de renta es de 12 meses.')
                            continue
                        item.meses_renta = nuevo_valor
                    
                    item.save()
                    
                except ValueError:
                    messages.error(request, "Valor inválido ingresado.")
                except CarritoItem.DoesNotExist:
                    messages.error(request, "Item no encontrado en el carrito.")
        
        return redirect('usuarios:ver_carrito')
    
    return redirect('usuarios:ver_carrito')

@login_required
def pedidos_pendientes(request):
    """Vista para mostrar solo los pedidos pendientes de pago"""
    if not request.user.rol == 'cliente':
        messages.error(request, 'Solo los clientes pueden acceder a esta sección.')
        return redirect('usuarios:inicio_cliente')
    
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    # Obtener solo pedidos pendientes de pago y que no estén vencidos
    ahora = timezone.now()
    pedidos = Pedido.objects.filter(
        cliente=cliente,
        estado_pedido_general='pendiente_pago',
        fecha_limite_pago__gt=ahora
    ).order_by('fecha_limite_pago')  # Ordenar por los que vencen primero
    
    # Procesar cada pedido para actualizar estados y calcular tiempos restantes
    pedidos_info = []
    for pedido in pedidos:
        # Verificar si el pedido está vencido en este momento
        if pedido.esta_vencido_pago():
            pedido.estado_pedido_general = 'pago_vencido'
            pedido.save()
            continue
        
        # Calcular tiempo restante
        tiempo_restante = pedido.get_tiempo_restante_pago()
        if tiempo_restante:
            horas = int(tiempo_restante.total_seconds() / 3600)
            minutos = int((tiempo_restante.total_seconds() % 3600) / 60)
            
            # Solo incluir si aún hay tiempo
            if horas > 0 or minutos > 0:
                pedidos_info.append({
                    'pedido': pedido,
                    'tiempo_restante_str': f"{horas}h {minutos}m",
                    'tiempo_restante_segundos': int(tiempo_restante.total_seconds()),
                    'detalles': pedido.detalles.all().select_related('producto'),
                    'total_con_iva': pedido.total * Decimal('1.19')
                })
    
    # Para solicitudes AJAX, devolver solo la información necesaria
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'cantidad_pedidos': len(pedidos_info),
            'pedidos': [{
                'id': info['pedido'].id_pedido,
                'tiempo_restante': info['tiempo_restante_str'],
                'total': float(info['pedido'].total)
            } for info in pedidos_info]
        })
    
    # Preparar contexto para la vista normal
    context = {
        'pedidos_info': pedidos_info,
        'cliente': cliente,
        'total_pendiente': sum(info['pedido'].total for info in pedidos_info),
        'cantidad_pedidos': len(pedidos_info)
    }
    
    return render(request, 'usuarios/pedidos_pendientes.html', context)
