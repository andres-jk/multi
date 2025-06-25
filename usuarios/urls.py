from django.urls import path
from . import views, views_divipola

app_name = 'usuarios'  # Agregar namespace

urlpatterns = [
    # Nueva URL para pedidos pendientes
    path('pedidos-pendientes/', views.pedidos_pendientes, name='pedidos_pendientes'),

    # DIVIPOLA API URLs
    path('api/departamentos/', views_divipola.get_departamentos, name='api_departamentos'),
    path('api/municipios/', views_divipola.get_municipios, name='api_municipios'),

    # Existing URL patterns...
    path('', views.inicio_cliente, name='inicio_cliente'),
    path('inicio/', views.inicio, name='inicio'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('carrito/cotizacion-pdf/', views.generar_cotizacion_pdf, name='generar_cotizacion_pdf'),
    path('carrito/remision-pdf/', views.generar_remision_pdf, name='generar_remision_pdf'),
    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('direcciones/agregar/', views.agregar_direccion, name='agregar_direccion'),
    path('direcciones/editar/<int:direccion_id>/', views.editar_direccion, name='editar_direccion'),
    path('direcciones/eliminar/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),
    path('checkout/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('recibo-pdf/<int:pedido_id>/', views.generar_recibo_pdf, name='generar_recibo_pdf'),
    path('carrito/pago/<int:pedido_id>/', views.pago_recibo, name='pago_recibo'),
    path('carrito/confirmacion/<int:pedido_id>/', views.confirmacion_pago, name='confirmacion_pago'),
    path('pedido/<int:pedido_id>/remision/', views.ver_remision, name='ver_remision'),
    path('pedido/<int:pedido_id>/generar-remision/', views.generar_remision_admin, name='generar_remision_admin'),
]
