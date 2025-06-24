from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.conf import settings
from django.http import HttpResponse
from django import forms
from django.utils import timezone
from pedidos.models import Pedido, DetallePedido
from productos.models import Producto
from recibos.models import ReciboObra
from .forms import UsuarioForm, ClienteForm, DireccionForm
from .models import CarritoItem, Cliente, Direccion

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

from .forms import MetodoPagoForm
from .models import Usuario, Cliente, MetodoPago, Direccion, CarritoItem

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
    
    # Calcular subtotales y total
    total = Decimal('0.00')
    for item in items_carrito:
        item.subtotal = item.producto.precio * item.cantidad * item.meses_renta
        total += item.subtotal
    
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
    cliente = get_object_or_404(Cliente, usuario=request.user)
    items = CarritoItem.objects.filter(cliente=cliente)
    
    for item in items:
        if item.reservado:
            item.liberar_reserva()
        item.delete()
    
    messages.success(request, 'Tu carrito ha sido limpiado.')
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

def generar_cotizacion_pdf(request):
    carrito = request.session.get('carrito', {})
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
        'nif': 'NIT 900.252.510-1',        'direccion': 'Cra. 128 #22A-45, Bogotá, Colombia',
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
        # Asegurar que value es una cadena
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
    col_widths = [250, 60, 60, 80, 80]  # Ajuste de anchos
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
    total_sin_iva = 0
    
    for item in carrito.values():
        if y < 180:  # Nueva página si no hay espacio
            p.showPage()
            draw_page_header()
            y = height - 100
            p.setFont("Helvetica", 9)
            tiempo_renta = item.get('tiempo_renta', item.get('meses', 1))
            precio_unitario = item['precio_unitario']
            subtotal = precio_unitario * item['cantidad'] * tiempo_renta
            
            # Dibujar fila
            p.setFillColor(colors.white)
            p.rect(40, y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
            p.setFillColor(colors.black)
            
            x = 40
            row_data = [
                item['nombre'][:40],
                str(item['cantidad']),
                str(tiempo_renta),
                f"${precio_unitario:,.2f}",
                f"${subtotal:,.2f}"
            ]
            
            for i, text in enumerate(row_data):
                p.drawString(x + 5, y - 15, text)
                x += col_widths[i]
            
            y -= row_height
    
    # Total
    y -= 20
    p.setFont("Helvetica-Bold", 10)
    p.drawString(width - 200, y, f"Total: ${total_sin_iva:,.2f}")
    
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
    """Vista para procesar el checkout"""
    # Obtener el cliente del usuario actual
    cliente = get_object_or_404(Cliente, usuario=request.user)
    items = CarritoItem.objects.filter(usuario=request.user)
    
    # Si no hay items en el carrito, redirigir al carrito
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('usuarios:ver_carrito')
    
    # Calcular el total del pedido
    total = sum(item.subtotal() for item in items)
    
    # Obtener las direcciones del cliente
    direcciones = Direccion.objects.filter(cliente=cliente)
    
    # Si no hay direcciones registradas, redirigir a agregar dirección
    if not direcciones.exists():
        messages.warning(request, 'Necesitas agregar una dirección de entrega antes de continuar.')
        return redirect('usuarios:agregar_direccion')
    
    if request.method == 'POST':
        # Validar que haya una dirección seleccionada
        direccion_id = request.POST.get('direccion')
        if not direccion_id:
            messages.error(request, 'Por favor selecciona una dirección de envío.')
            return render(request, 'usuarios/checkout.html', {
                'items': items,
                'direcciones': direcciones,
                'total': total
            })
        
        try:
            direccion = get_object_or_404(Direccion, id=direccion_id, cliente=cliente)
            notas = request.POST.get('notas', '')
            
            # Crear el pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                direccion_entrega=f"{direccion.calle}, {direccion.ciudad}, {direccion.departamento}",
                estado_pedido_general='pendiente_pago',
                total=total,
                notas=notas,
                fecha=timezone.now()
            )
            
            # Crear los detalles del pedido y actualizar el inventario
            for item in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    meses_renta=item.meses_renta,
                    precio_unitario=item.producto.precio,
                )
                
                # Actualizar el inventario
                item.producto.cantidad_disponible -= item.cantidad
                item.producto.cantidad_en_renta += item.cantidad
                item.producto.save()
            
            # Limpiar el carrito
            items.delete()
            messages.success(request, 'Tu pedido ha sido creado exitosamente. Por favor, procede con el pago.')
            return redirect('usuarios:pago_recibo', pedido_id=pedido.id_pedido)
            
        except Exception as e:
            # Si algo falla, hacer rollback manualmente
            if 'pedido' in locals():
                # Revertir cambios en el inventario
                for detalle in pedido.detalles.all():
                    if detalle.producto.cantidad_en_renta >= detalle.cantidad:
                        detalle.producto.cantidad_en_renta -= detalle.cantidad
                        detalle.producto.cantidad_disponible += detalle.cantidad
                        detalle.producto.save()
                pedido.delete()
            messages.error(request, f'Hubo un error al procesar tu pedido: {str(e)}')
            return redirect('usuarios:checkout')
    
    return render(request, 'usuarios/checkout.html', {
        'items': items,
        'direcciones': direcciones,
        'total': total
    })

@login_required
def mis_pedidos(request):
    # Obtenemos el cliente asociado al usuario actual
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    # Obtenemos todos los pedidos del cliente ordenados por fecha descendente
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    
    # Contexto para la plantilla
    context = {
        'pedidos': pedidos,
        'cliente': cliente,
    }
    
    return render(request, 'usuarios/mis_pedidos.html', context)

@login_required
def detalle_pedido(request, pedido_id):
    """Vista para mostrar el detalle de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
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
    # Obtener el pedido existente
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, cliente__usuario=request.user)
    
    if pedido.estado_pedido_general == 'pagado':
        messages.info(request, "Este pedido ya ha sido pagado.")
        return redirect('usuarios:confirmacion_pago', pedido_id=pedido.id_pedido)
    
    # Obtener los detalles del pedido
    detalles = pedido.detalles.all().select_related('producto')
    
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST, request.FILES)
        if form.is_valid():
            metodo_pago = form.save(commit=False)
            metodo_pago.usuario = request.user
            metodo_pago.monto = pedido.total
            metodo_pago.save()
            
            # Actualizar el pedido con el método de pago
            pedido.metodo_pago = str(metodo_pago.get_tipo_display())
            if metodo_pago.tipo == 'efectivo':
                pedido.estado_pedido_general = 'pagado'
            else:
                pedido.estado_pedido_general = 'pendiente_verificacion'
            pedido.save()
            
            messages.success(request, "Tu pago ha sido registrado correctamente.")
            return redirect('usuarios:confirmacion_pago', pedido_id=pedido.id_pedido)
    else:
        form = MetodoPagoForm()
    
    # Datos bancarios de la empresa
    datos_bancarios = {
        'banco': 'Bancolombia',
        'tipo_cuenta': 'Cuenta de Ahorros',
        'numero_cuenta': '123456789',
        'titular': 'MultiAndamios S.A.S',
        'nit': '900.123.456-7'
    }
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'pago_form': form,
        'datos_bancarios': datos_bancarios,
        'total': pedido.total
    }
    
    return render(request, 'usuarios/pago.html', context)

@login_required
def confirmacion_pago(request, pedido_id):
    # Obtener el pedido y verificar que pertenece al usuario actual
    pedido = get_object_or_404(Pedido, 
                              id_pedido=pedido_id, 
                              cliente__usuario=request.user)
    
    # Obtener los detalles del pedido
    detalles = DetallePedido.objects.filter(pedido=pedido)
    
    # Preparar el contexto
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'cliente': pedido.cliente,
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
        cliente = get_object_or_404(Cliente, usuario=request.user)
        
        for key, value in request.POST.items():
            if key.startswith(('cantidad_', 'meses_')):
                try:
                    item_id = int(key.split('_')[1])
                    nuevo_valor = int(value)
                    if nuevo_valor < 1:
                        continue
                        
                    item = get_object_or_404(CarritoItem, id=item_id, cliente=cliente)
                    
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
                                         f'El máximo de meses de renta es 12.')
                            continue
                        item.meses_renta = nuevo_valor
                    
                    item.save()
                
                except (ValueError, CarritoItem.DoesNotExist):
                    continue
        
        messages.success(request, 'Carrito actualizado correctamente.')
    
    return redirect('usuarios:ver_carrito')
