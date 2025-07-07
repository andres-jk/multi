from django.urls import path, include
from . import views
from . import views_entregas
from . import views_devoluciones

app_name = 'pedidos'  # Agregar namespace

urlpatterns = [
    # URLs para administradores y empleados
    path('admin/clientes/', views.lista_clientes, name='lista_clientes'),  # Lista de clientes (admin)
    path('admin/clientes/agregar/', views.agregar_cliente, name='agregar_cliente'),  # Agregar cliente (admin)
    path('admin/clientes/cambiar_estado/<int:usuario_id>/', views.cambiar_estado_cliente, name='cambiar_estado_cliente'),
    path('admin/productos/', views.admin_productos, name='admin_productos'),  # Admin productos (admin)
    path('admin/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin/productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('admin/productos/cambiar_estado/<int:producto_id>/', views.cambiar_estado_producto, name='cambiar_estado_producto'),
    path('', views.lista_pedidos, name='lista_pedidos'),  # Lista de pedidos (admin)
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),  # Detalle de pedido (admin)
    path('<int:pedido_id>/aprobar-pago/', views.aprobar_pago, name='aprobar_pago'),  # Aprobar/rechazar pago
    path('<int:pedido_id>/remision/', views.generar_remision_pdf, name='generar_remision_pdf'),
    path('<int:pedido_id>/factura/', views.generar_factura_pdf, name='generar_factura_pdf'),
    
    # URLs para clientes
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),  # Lista de pedidos del cliente
    path('mis-pedidos/<int:pedido_id>/', views.detalle_mi_pedido, name='detalle_mi_pedido'),  # Detalle para el cliente
    path('crear/', views.crear_pedido, name='crear_pedido'),  # Crear pedido (disponible para clientes)
    path('<int:pedido_id>/programar-devolucion/', views.programar_devolucion, name='programar_devolucion'),  # Programar devolución
    
    # URLs para devoluciones parciales y extensiones de renta
    path('<int:pedido_id>/devolucion-parcial/', views_devoluciones.registrar_devolucion_parcial, name='registrar_devolucion_parcial'),
    path('<int:pedido_id>/extender-renta/', views_devoluciones.extender_renta, name='extender_renta'),
    path('<int:pedido_id>/seleccion-devolucion-parcial/', views_devoluciones.seleccion_devolucion_parcial, name='seleccion_devolucion_parcial'),
    path('<int:pedido_id>/cambiar-estado-productos/', views_devoluciones.cambiar_estado_productos_pedido, name='cambiar_estado_productos_pedido'),
    
    # URLs para reportes de tiempo de renta
    path('mis-pedidos/tiempo/', views.mis_pedidos_tiempo, name='mis_pedidos_tiempo'),  # Tiempo restante para clientes
    path('admin/tiempo/reporte/', views.reporte_tiempo_global, name='reporte_tiempo_global'),  # Reporte global para admin
    path('admin/tiempo/<int:pedido_id>/', views.detalle_tiempo_pedido, name='detalle_tiempo_pedido'),  # Detalle de tiempo
    path('admin/tiempo/notificaciones/', views.notificaciones_vencimiento, name='notificaciones_vencimiento'),  # Notificaciones
    path('admin/tiempo/dashboard/', views.dashboard_tiempo, name='dashboard_tiempo'),  # Dashboard de tiempo

    # URLs de entregas
    path('entregas/', include('pedidos.urls_entregas')),
]

# Las rutas completas después de la configuración son:
# /panel/admin/clientes/ - Lista de clientes (admin)
# /panel/admin/productos/ - Admin productos (admin)
# /panel/ - Lista de pedidos (admin)
# /panel/<id>/ - Detalle de pedido (admin)
# /panel/mis-pedidos/ - Lista de pedidos (cliente)
# /panel/mis-pedidos/<id>/ - Detalle de pedido (cliente)
# /panel/crear/ - Crear pedido (cliente)

