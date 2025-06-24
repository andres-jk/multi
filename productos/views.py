from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Producto

@login_required
def catalogo(request):
    query = request.GET.get('busqueda', '')
    productos_list = Producto.objects.all()
    
    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tipo_renta__icontains=query)
        )
    
    # Configuración de paginación
    paginator = Paginator(productos_list, 10)  # 10 productos por página
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    return render(request, 'productos/catalogo.html', {
        'productos': productos,
        'query': query,
    })

@login_required
def detalle_producto(request, producto_id):
    """Vista para mostrar el detalle de un producto específico"""
    producto = get_object_or_404(Producto, id_producto=producto_id)
    return render(request, 'productos/detalle_producto.html', {
        'producto': producto
    })
