from django.urls import path
from . import views_entregas

urlpatterns = [
    # Panel de entregas para empleados
    path('panel/', views_entregas.panel_entregas, name='panel_entregas'),
    path('pedidos-listos/', views_entregas.pedidos_listos_entrega, name='pedidos_listos_entrega'),
    path('detalle/<int:entrega_id>/', views_entregas.detalle_entrega, name='detalle_entrega'),
    path('programar/<int:pedido_id>/', views_entregas.programar_entrega, name='programar_entrega'),
    
    # Gestión de recorridos
    path('iniciar/<int:entrega_id>/', views_entregas.iniciar_recorrido, name='iniciar_recorrido'),
    path('seguimiento/<int:entrega_id>/', views_entregas.seguimiento_entrega, name='seguimiento_entrega'),
    path('confirmar/<int:entrega_id>/', views_entregas.confirmar_entrega, name='confirmar_entrega'),
    
    # APIs para actualizaciones en tiempo real
    path('api/actualizar-ubicacion/', views_entregas.actualizar_ubicacion, name='actualizar_ubicacion'),
    path('api/ubicacion/<int:pedido_id>/', views_entregas.api_ubicacion_entrega, name='api_ubicacion_entrega'),
    
    # Seguimiento para clientes
    path('cliente/seguimiento/<int:pedido_id>/', views_entregas.seguimiento_cliente, name='seguimiento_cliente'),
]
