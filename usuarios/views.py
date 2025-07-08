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
from .forms import (PerfilForm, ClienteForm, DireccionForm, EmpleadoForm,
                    RegistroForm) # Asegúrate de que RegistroForm venga de aquí o defínelo aquí.
from .models import Usuario, Cliente, MetodoPago, Direccion, CarritoItem
from .models_divipola import Departamento, Municipio

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import mm, inch, cm

from datetime import datetime, timedelta
import uuid
import json
import os
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
        "dias_renta": <int, opcional>
    }
    Si la cantidad es 0, el DetallePedido será eliminado.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            detalle_pedido_id = data.get('detalle_pedido_id')
            nueva_cantidad = data.get('cantidad')
            nuevos_dias_renta = data.get('dias_renta')

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

                # 2. Actualizar los días de renta si se proporcionan y son válidos
                if nuevos_dias_renta is not None:
                    if not isinstance(nuevos_dias_renta, int) or nuevos_dias_renta < 1:
                        return JsonResponse({'success': False, 'message': 'Días de renta inválidos. Debe ser un número entero positivo.'}, status=400)
                    detalle_pedido.dias_renta = nuevos_dias_renta

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
                                     'nuevos_dias_renta': detalle_pedido.dias_renta,
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

# FUNCIONES OBSOLETAS REMOVIDAS - SE USAN LAS VERSIONES V2

def _generate_common_pdf(request, document_type, items_to_include):
    """
    Función genérica para generar PDFs de cotización o remisión.
    VERSIÓN OPTIMIZADA - 2025-01-06 - LOGGING REDUCIDO
    :param document_type: 'cotizacion' o 'remision'
    :param items_to_include: QuerySet de CarritoItem (para cotización) o items reservados (para remisión)
    """
    
    if not items_to_include or not items_to_include.exists():
        messages.error(request, f'El carrito está vacío o no hay items reservados para la {document_type}.')
        return redirect('usuarios:ver_carrito')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Información del receptor (cliente) - Mejorado para obtener datos completos
    user = request.user
    direccion_principal = None
    telefono_usuario = ""
    direccion_completa = ""
    
    # Intentar obtener datos más completos del usuario con verificaciones de seguridad
    try:
        if hasattr(user, 'direcciones'):
            direccion_principal = user.direcciones.filter(principal=True).first()
            
            if direccion_principal and hasattr(direccion_principal, 'direccion'):
                direccion_partes = []
                if direccion_principal.direccion:
                    direccion_partes.append(str(direccion_principal.direccion))
                if hasattr(direccion_principal, 'municipio') and direccion_principal.municipio and hasattr(direccion_principal.municipio, 'nombre'):
                    direccion_partes.append(str(direccion_principal.municipio.nombre))
                if hasattr(direccion_principal, 'departamento') and direccion_principal.departamento and hasattr(direccion_principal.departamento, 'nombre'):
                    direccion_partes.append(str(direccion_principal.departamento.nombre))
                direccion_completa = ", ".join(direccion_partes) if direccion_partes else "N/A"
            else:
                direccion_completa = getattr(user, 'direccion_texto', getattr(user, 'direccion', 'N/A'))
        else:
            direccion_completa = getattr(user, 'direccion_texto', getattr(user, 'direccion', 'N/A'))
        
        telefono_usuario = getattr(user, 'telefono', 'N/A')
        if hasattr(user, 'cliente') and user.cliente:
            telefono_usuario = getattr(user.cliente, 'telefono', telefono_usuario)
            
    except Exception as e:
        print(f"[ERROR PDF] Error obteniendo datos del usuario: {e}")
        direccion_completa = "N/A"
        telefono_usuario = "N/A"

    receptor_info = {
        'nombre': f"{user.first_name} {user.last_name}".strip() or "Cliente",
        'nif': str(getattr(user, 'numero_identidad', 'N/A')),
        'direccion': str(direccion_completa),
        'telefono': str(telefono_usuario),
        'email': str(user.email or 'N/A')
    }

    # Dibujar todas las secciones con espaciado optimizado y verificaciones de seguridad
    current_y = height - 10  # Comenzar muy cerca del borde superior
    
    try:
        # 1. Encabezado
        current_y = _draw_pdf_header_v2(p, width, current_y, document_type.upper())
        
        # 2. Información de empresa y cliente en diseño compacto
        current_y = _draw_company_client_info_v2(p, current_y, width, EMISOR_INFO, receptor_info)
        
        # 3. Información del documento
        current_y = _draw_document_info_v2(p, current_y, width, document_type)
        
        # 4. Tabla de productos con verificaciones de seguridad ultra-robustas
        headers = ["Descripción", "Cant.", "Período", "Precio Unit.", "Subtotal"]
        col_widths = [280, 50, 80, 80, 80]
        
        # Verificaciones ultra-robustas antes de procesar
        if not headers or not isinstance(headers, (list, tuple)):
            print(f"[ERROR PDF] Headers inválido: {headers}")
            raise ValueError("Headers debe ser una lista válida")
            
        if not col_widths or not isinstance(col_widths, (list, tuple)):
            print(f"[ERROR PDF] Col_widths inválido: {col_widths}")
            raise ValueError("Col_widths debe ser una lista válida")
            
        if len(headers) != len(col_widths):
            print(f"[ERROR PDF] Longitudes no coinciden: headers={len(headers)}, col_widths={len(col_widths)}")
            raise ValueError("Headers y col_widths deben tener la misma longitud")
            
        # Verificar que no hay elementos None en las listas
        for i, header in enumerate(headers):
            if header is None:
                headers[i] = f"Col_{i}"
                
        for i, width in enumerate(col_widths):
            if width is None:
                col_widths[i] = 50  # Ancho por defecto
        
        current_y, total_sin_iva, peso_total = _draw_products_table_v2(
            p, items_to_include, headers, col_widths, 40, current_y, document_type
        )
        
        # 5. Cálculo de costos de envío
        costo_transporte = _calculate_shipping_cost(request.user)
        
        # 6. Totales
        current_y = _draw_totals_section_v2(
            p, width, current_y, total_sin_iva, costo_transporte, document_type
        )
        
        # 7. Observaciones
        current_y = _draw_observations_section_v2(p, current_y, width, document_type, costo_transporte)
        
        # 8. Firmas
        current_y = _draw_signatures_section_v2(p, width, current_y)
        
        # 9. Pie de página
        _draw_footer_v2(p, width)
        
        p.save()
        return response
        
    except Exception as e:
        print(f"[ERROR PDF] Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Error interno al generar la {document_type}: {str(e)}')
        return redirect('usuarios:ver_carrito')

@login_required
def generar_cotizacion_pdf(request):
    try:
        # Obtener items del carrito
        items_carrito = CarritoItem.objects.filter(usuario=request.user)
        
        if not items_carrito.exists():
            messages.warning(request, 'No hay productos en el carrito para generar la cotización.')
            return redirect('usuarios:ver_carrito')

        return _generate_common_pdf(request, 'cotizacion', items_carrito)
        
    except Exception as e:
        print(f"[ERROR COTIZACION] Error en generar_cotizacion_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
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
    # Filtrar items del carrito con productos válidos (no None)
    carrito_items = CarritoItem.objects.filter(
        usuario=request.user,
        producto__isnull=False
    ).select_related('producto')
    
    # Limpiar items del carrito que tengan productos None (por si acaso)
    CarritoItem.objects.filter(
        usuario=request.user,
        producto__isnull=True
    ).delete()
    
    if not carrito_items.exists():
        messages.error(request, 'Tu carrito está vacío. Agrega productos antes de proceder al pago.')
        return redirect('usuarios:ver_carrito')
    
    departamentos = Departamento.objects.all().order_by('nombre')

    # Calcular subtotal con validación adicional
    subtotal = Decimal('0.00')
    for item in carrito_items:
        if item.producto:  # Verificar que el producto existe
            subtotal += item.subtotal
    
    iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Get transport cost from user's main address or default
    costo_transporte = _calculate_shipping_cost(request.user)
    
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
                    # Verificar que el producto existe
                    if not item.producto:
                        continue  # Saltar items sin producto válido
                        
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

@login_required
def calcular_costo_envio_ajax(request):
    """Vista AJAX para calcular el costo de envío basado en el municipio seleccionado"""
    if request.method == 'GET':
        municipio_id = request.GET.get('municipio_id')
        
        if not municipio_id:
            return JsonResponse({'error': 'ID de municipio requerido'}, status=400)
        
        try:
            municipio = Municipio.objects.get(id=municipio_id)
            costo_transporte = municipio.costo_transporte or Decimal('15000.00')
            
            # Recalcular totales del carrito
            carrito_items = CarritoItem.objects.filter(
                usuario=request.user,
                producto__isnull=False
            ).select_related('producto')
            
            subtotal = Decimal('0.00')
            for item in carrito_items:
                if item.producto:
                    subtotal += item.subtotal
            
            iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_con_transporte = subtotal + iva + costo_transporte
            
            return JsonResponse({
                'success': True,
                'costo_transporte': float(costo_transporte),
                'costo_transporte_formatted': f"${costo_transporte:,.0f}",
                'subtotal': float(subtotal),
                'subtotal_formatted': f"${subtotal:,.0f}",
                'iva': float(iva),
                'iva_formatted': f"${iva:,.0f}",
                'total': float(total_con_transporte),
                'total_formatted': f"${total_con_transporte:,.0f}",
                'municipio_nombre': municipio.nombre,
                'departamento_nombre': municipio.departamento.nombre
            })
            
        except Municipio.DoesNotExist:
            return JsonResponse({'error': 'Municipio no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para cargar municipios basada en el departamento seleccionado (AJAX)
def cargar_municipios(request):
    departamento_id = request.GET.get('departamento_id')
    municipios = []
    if departamento_id:
        try:
            municipios = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre').values('id', 'nombre', 'codigo')
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

# === FUNCIONES AUXILIARES PARA GENERACIÓN DE PDF V2 (DISEÑO MEJORADO) ===

def _draw_pdf_header_v2(p, width, current_y, title):
    """Encabezado mejorado y más compacto."""
    header_height = 40  # Reducido de 50 a 40
    
    # Fondo del encabezado
    p.setFillColor(colors.HexColor("#1A1228"))
    p.rect(0, current_y - header_height, width, header_height, fill=1, stroke=0)
    
    # Título principal
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)  # Reducido de 20 a 18
    p.drawCentredString(width / 2, current_y - 20, title)
    
    # Nombre de la empresa
    p.setFont("Helvetica-Bold", 10)  # Reducido de 12 a 10
    p.drawCentredString(width / 2, current_y - 35, "MULTIANDAMIOS S.A.S.")
    
    return current_y - header_height - 5  # Reducido el espaciado de 15 a 5

def _draw_company_client_info_v2(p, current_y, width, emisor, receptor):
    """Información de empresa y cliente en diseño horizontal compacto."""
    
    # Dimensiones para toda la sección (más compacta)
    section_height = 70  # Reducido de 80 a 70
    margin = 30
    section_width = width - (2 * margin)
    
    # Marco principal
    p.setLineWidth(1.5)
    p.setStrokeColor(colors.HexColor("#333333"))
    p.rect(margin, current_y - section_height, section_width, section_height, stroke=1, fill=0)
    
    # Dividir en dos columnas iguales
    col_width = section_width / 2
    divider_x = margin + col_width
    
    # Línea divisoria
    p.setStrokeColor(colors.HexColor("#CCCCCC"))
    p.line(divider_x, current_y - section_height, divider_x, current_y)
    
    # COLUMNA IZQUIERDA - PROVEEDOR
    # Encabezado proveedor (más pequeño)
    p.setFillColor(colors.HexColor("#1A1228"))
    p.rect(margin, current_y - 18, col_width, 18, fill=1, stroke=0)  # Reducido de 20 a 18
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 9)  # Reducido de 10 a 9
    p.drawCentredString(margin + col_width/2, current_y - 12, "DATOS DEL PROVEEDOR")
    
    # Datos del proveedor en formato compacto
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 7)  # Reducido de 8 a 7
    y_pos = current_y - 28  # Ajustado
    
    provider_lines = [
        f"{emisor['nombre']} | NIT: {emisor['nif']}",
        f"Dir: {emisor['direccion'][:40]}",
        f"Tel: {emisor['telefono']} | Email: {emisor['email'][:25]}"
    ]
    
    for line in provider_lines:
        p.drawString(margin + 20, y_pos, line)  # Aumentado margen de 15 a 20 para mejor centrado
        y_pos -= 10  # Reducido de 12 a 10
    
    # COLUMNA DERECHA - CLIENTE
    # Encabezado cliente (más pequeño)
    p.setFillColor(colors.HexColor("#FFD600"))
    p.rect(divider_x, current_y - 18, col_width, 18, fill=1, stroke=0)  # Reducido de 20 a 18
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)  # Reducido de 10 a 9
    p.drawCentredString(divider_x + col_width/2, current_y - 12, "DATOS DEL CLIENTE")
    
    # Datos del cliente en formato compacto
    p.setFont("Helvetica", 7)  # Reducido de 8 a 7
    y_pos = current_y - 28  # Ajustado
    
    client_lines = [
        f"{receptor['nombre']} | Doc: {receptor['nif']}",
        f"Dir: {receptor['direccion'][:40]}",
        f"Tel: {receptor['telefono']} | Email: {receptor['email'][:25]}"
    ]
    
    for line in client_lines:
        p.drawString(divider_x + 30, y_pos, line)  # Aumentado margen de 15 a 20 para mejor centrado
        y_pos -= 10  # Reducido de 12 a 10
    
    return current_y - section_height - 5  # Reducido el espaciado de 15 a 5

def _draw_document_info_v2(p, current_y, width, document_type):
    """Información del documento en diseño horizontal."""
    
    info_height = 25  # Reducido de 30 a 25
    margin = 30
    info_width = width - (2 * margin)
    
    # Marco
    p.setLineWidth(1)
    p.setStrokeColor(colors.HexColor("#FFD600"))
    p.setFillColor(colors.HexColor("#FFFBCC"))
    p.rect(margin, current_y - info_height, info_width, info_height, stroke=1, fill=1)
    
    # Información en una línea
    fecha = datetime.now()
    numero_documento = f"{document_type.upper()[:3]}-{uuid.uuid4().hex[:8].upper()}"
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 8)  # Reducido de 9 a 8
    
    # Fecha (izquierda)
    p.drawString(margin + 10, current_y - 16, f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}")
    
    # Número (centro)
    p.drawCentredString(width / 2, current_y - 16, f"Número: {numero_documento}")
    
    # Validez/Hora (derecha)
    validez_text = "Validez: 15 días" if document_type == 'cotizacion' else f"Hora: {fecha.strftime('%H:%M:%S')}"
    p.drawRightString(margin + info_width - 10, current_y - 16, validez_text)
    
    return current_y - info_height - 5  # Reducido el espaciado de 15 a 5

def _draw_products_table_v2(p, items, headers, col_widths, x_start, current_y, document_type):
    """Tabla de productos con diseño mejorado y espaciado correcto."""
    
    # Verificaciones de seguridad
    if not headers or not col_widths:
        raise ValueError("Headers o col_widths no pueden ser None")
    
    if len(headers) != len(col_widths):
        raise ValueError("Headers y col_widths deben tener la misma longitud")
    
    if not items:
        raise ValueError("Items no puede ser None")
    
    # Encabezado de la tabla
    row_height = 25
    header_y = current_y
    
    # Fondo del encabezado
    p.setFillColor(colors.HexColor("#1A1228"))
    p.rect(x_start, header_y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
    
    # Texto del encabezado
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)
    
    x = x_start
    for i, header in enumerate(headers):
        if i < len(col_widths):  # Verificación adicional de seguridad
            header_x = x + col_widths[i] / 2
            p.drawCentredString(header_x, header_y - 16, str(header))
            x += col_widths[i]
    
    # Filas de productos
    current_y = header_y - row_height
    row_height = 22
    total_sin_iva = Decimal('0.00')
    peso_total = Decimal('0.00')
    row_count = 0
    
    p.setStrokeColor(colors.HexColor("#DDDDDD"))
    
    for item in items:
        # Verificar si necesitamos nueva página
        if current_y < 120:
            p.showPage()
            current_y = 700
            current_y = _draw_pdf_header_v2(p, 612, current_y, document_type.upper())
            # Redibujar encabezado de tabla
            p.setFillColor(colors.HexColor("#1A1228"))
            p.rect(x_start, current_y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 10)
            x = x_start
            for i, header in enumerate(headers):
                if i < len(col_widths):
                    header_x = x + col_widths[i] / 2
                    p.drawCentredString(header_x, current_y - 16, str(header))
                    x += col_widths[i]
            current_y -= row_height
            row_count = 0
        
        # Verificaciones de seguridad para el item
        try:
            # Verificar que el item tenga los atributos necesarios
            if not hasattr(item, 'producto') or not item.producto:
                print(f"[DEBUG] Item sin producto: {item}")
                continue
                
            if not hasattr(item, 'cantidad') or item.cantidad is None:
                print(f"[DEBUG] Item sin cantidad: {item}")
                continue
            
            # Cálculos del item con verificaciones
            subtotal = getattr(item, 'subtotal', Decimal('0.00'))
            if subtotal is None:
                subtotal = Decimal('0.00')
            
            total_sin_iva += subtotal
            
            # Peso total con verificación
            try:
                if hasattr(item, 'peso_total'):
                    peso_item = item.peso_total
                    if peso_item is not None:
                        peso_total += peso_item
            except Exception as e:
                print(f"[DEBUG] Error calculando peso: {e}")
            
            # Fondo alternado
            if row_count % 2 == 0:
                p.setFillColor(colors.HexColor("#F9F9F9"))
            else:
                p.setFillColor(colors.white)
            
            p.rect(x_start, current_y - row_height, sum(col_widths), row_height, fill=1, stroke=1)
            
            # Contenido de la fila
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 9)
            
            # Obtener datos del item con verificaciones
            precio_unitario = getattr(item.producto, 'precio_diario', Decimal('0.00'))
            if precio_unitario is None:
                precio_unitario = Decimal('0.00')
            
            # Descripción de días con verificación
            try:
                if hasattr(item, 'get_descripcion_dias'):
                    duracion_texto = item.get_descripcion_dias()
                elif hasattr(item, 'dias_renta'):
                    duracion_texto = f"{item.dias_renta} días"
                else:
                    duracion_texto = "N/A"
            except Exception as e:
                print(f"[DEBUG] Error obteniendo descripción días: {e}")
                duracion_texto = "N/A"
            
            # Preparar datos de la fila
            row_data = [
                str(item.producto.nombre)[:45] if item.producto.nombre else "Sin nombre",
                str(item.cantidad),
                str(duracion_texto),
                f"${precio_unitario:,.0f}",
                f"${subtotal:,.0f}"
            ]
            
            # Dibujar datos con verificaciones ultra-seguras
            x = x_start
            for i, text in enumerate(row_data):
                # Triple verificación para evitar 'NoneType' object is not subscriptable
                if (i < len(col_widths) and 
                    col_widths is not None and 
                    isinstance(col_widths, (list, tuple)) and 
                    i < len(col_widths) and 
                    col_widths[i] is not None):
                    
                    try:
                        if i == 0:  # Descripción alineada a la izquierda
                            p.drawString(x + 5, current_y - 14, str(text))
                        else:  # Números centrados
                            text_width = p.stringWidth(str(text), "Helvetica", 9)
                            x_centered = x + (col_widths[i] - text_width) / 2
                            p.drawString(x_centered, current_y - 14, str(text))
                        x += col_widths[i]
                    except Exception as cell_error:
                        print(f"[DEBUG] Error dibujando celda {i}: {cell_error}")
                        # Usar ancho por defecto si hay error
                        x += 50
                        continue
            
            current_y -= row_height
            row_count += 1
            
        except Exception as e:
            print(f"[DEBUG] Error procesando item: {e}")
            # Continuar con el siguiente item en caso de error
            continue
    
    return current_y - 10, total_sin_iva, peso_total  # Reducido el espaciado de 15 a 10

def _calculate_shipping_cost(user):
    """Calcula el costo de envío basado en la ubicación del usuario."""
    from .models_divipola import Municipio
    
    try:
        # Intentar obtener el costo de transporte del municipio del usuario
        # Aquí asumimos que el usuario tiene una dirección principal
        if hasattr(user, 'direcciones') and user.direcciones.filter(principal=True).exists():
            direccion_principal = user.direcciones.filter(principal=True).first()
            if direccion_principal and direccion_principal.municipio:
                return direccion_principal.municipio.costo_transporte
        
        # Si no tiene dirección o municipio definido, usar costo por defecto
        return Decimal('15000.00')  # Costo base por defecto
        
    except Exception:
        return Decimal('15000.00')  # Costo por defecto en caso de error

def _draw_totals_section_v2(p, width, current_y, total_sin_iva, costo_transporte, document_type):
    """Sección de totales mejorada y más compacta."""
    
    totals_width = 250
    totals_x = width - totals_width - 30
    
    if document_type == 'cotizacion':
        totals_height = 85  # Reducido de 100 a 85
    else:
        totals_height = 60  # Reducido de 70 a 60
    
    # Marco principal
    p.setLineWidth(1.5)
    p.setStrokeColor(colors.HexColor("#333333"))
    p.rect(totals_x, current_y - totals_height, totals_width, totals_height, stroke=1, fill=0)
    
    # Encabezado (más pequeño)
    p.setFillColor(colors.HexColor("#F0F0F0"))
    p.rect(totals_x, current_y - 18, totals_width, 18, fill=1, stroke=1)  # Reducido de 20 a 18
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 9)  # Reducido de 10 a 9
    p.drawCentredString(totals_x + totals_width/2, current_y - 12, "RESUMEN DE COSTOS")
    
    # Líneas de totales
    y_line = current_y - 32  # Ajustado
    p.setFont("Helvetica", 8)  # Reducido de 9 a 8
    
    # Subtotal productos
    p.drawString(totals_x + 10, y_line, "Subtotal productos:")
    p.drawRightString(totals_x + totals_width - 10, y_line, f"${total_sin_iva:,.0f}")
    y_line -= 15  # Reducido de 18 a 15
    
    if document_type == 'cotizacion':
        # Costo de envío
        p.drawString(totals_x + 10, y_line, "Costo de envío:")
        p.drawRightString(totals_x + totals_width - 10, y_line, f"${costo_transporte:,.0f}")
        y_line -= 15  # Reducido de 18 a 15
        
        # IVA con transporte
        subtotal_con_transporte = total_sin_iva + costo_transporte
        iva_total = (subtotal_con_transporte * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_final = subtotal_con_transporte + iva_total
    else:
        # IVA sin transporte
        iva_total = (total_sin_iva * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_final = total_sin_iva + iva_total
    
    # IVA
    p.drawString(totals_x + 10, y_line, "IVA (19%):")
    p.drawRightString(totals_x + totals_width - 10, y_line, f"${iva_total:,.0f}")
    y_line -= 17  # Reducido de 20 a 17
    
    # Total final destacado
    p.setFillColor(colors.HexColor("#FFD600"))
    p.rect(totals_x, y_line - 3, totals_width, 16, fill=1, stroke=1)  # Reducido de 18 a 16
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)  # Reducido de 11 a 10
    p.drawString(totals_x + 10, y_line + 4, "TOTAL:")
    p.drawRightString(totals_x + totals_width - 10, y_line + 4, f"${total_final:,.0f}")
    
    return current_y - totals_height - 10  # Reducido el espaciado de 20 a 10

def _draw_observations_section_v2(p, current_y, width, document_type, costo_transporte):
    """Sección de observaciones con diseño compacto."""
    
    if document_type == 'cotizacion':
        obs_height = 80
        margin = 30
        totals_width = 250  # Definir aquí también
        obs_width = width - totals_width - 60  # Al lado de los totales
        
        # Marco
        p.setLineWidth(1)
        p.setStrokeColor(colors.HexColor("#CCCCCC"))
        p.rect(margin, current_y - obs_height, obs_width, obs_height, stroke=1, fill=0)
        
        # Encabezado
        p.setFillColor(colors.HexColor("#F8F8F8"))
        p.rect(margin, current_y - 18, obs_width, 18, fill=1, stroke=1)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 9)
        p.drawString(margin + 8, current_y - 12, "CONDICIONES Y OBSERVACIONES")
        
        # Observaciones compactas
        p.setFont("Helvetica", 8)
        observations = [
            "• Cotización válida por 15 días calendario",
            "• Precios NO incluyen IVA (19%)",
            f"• Envío estimado: ${costo_transporte:,.0f}",
            "• Pago: 50% anticipo, 50% contra entrega",
            "• Entrega: 1-3 días hábiles",
            "• Devolución en mismo estado"
        ]
        
        y_obs = current_y - 30
        for obs in observations:
            p.drawString(margin + 8, y_obs, obs)
            y_obs -= 9
        
        return current_y - obs_height - 15
    else:
        return current_y - 20

def _draw_signatures_section_v2(p, width, current_y):
    """Sección de firmas compacta."""
    
    sig_height = 60
    margin = 30
    sig_width = width - (2 * margin)
    
    # Marco
    p.setLineWidth(1)
    p.setStrokeColor(colors.HexColor("#CCCCCC"))
    p.rect(margin, current_y - sig_height, sig_width, sig_height, stroke=1, fill=0)
    
    # Dividir en dos columnas
    col_width = sig_width / 2
    divider_x = margin + col_width
    
    # Línea divisoria
    p.line(divider_x, current_y - sig_height, divider_x, current_y)
    
    # Firmas
    p.setFont("Helvetica", 8)
    
    # Firma del proveedor
    p.drawString(margin + 10, current_y - 25, "Firma y Sello Proveedor:")
    p.line(margin + 10, current_y - 45, divider_x - 10, current_y - 45)
    
    # Firma del cliente
    p.drawString(divider_x + 10, current_y - 25, "Firma Cliente:")
    p.line(divider_x + 10, current_y - 45, margin + sig_width - 10, current_y - 45)
    
    return current_y - sig_height - 15

def _draw_footer_v2(p, width):
    """Pie de página corporativo."""
    
    footer_height = 25
    
    # Fondo del pie
    p.setFillColor(colors.HexColor("#1A1228"))
    p.rect(0, 0, width, footer_height, fill=1, stroke=0)
    
    # Texto del pie
    p.setFillColor(colors.white)
    p.setFont("Helvetica", 8)
    footer_text = "MULTIANDAMIOS S.A.S. - Soluciones en alquiler de andamios y equipos industriales"
    p.drawCentredString(width / 2, 12, footer_text)

def test_divipola_view(request):
    """Vista simple para probar DIVIPOLA en el navegador"""
    from django.http import HttpResponse
    import os
    
    # Leer el archivo HTML de test
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_divipola_browser.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HttpResponse(html_content)