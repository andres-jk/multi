from django.urls import path
from . import views

app_name = 'recibos'

urlpatterns = [
    path('lista/', views.lista_recibos, name='lista_recibos'),
    path('diagnostico/', views.diagnostico_devoluciones, name='diagnostico_devoluciones'),
    path('crear/<int:pedido_id>/', views.crear_recibo, name='crear_recibo'),
    path('crear-multiple/<int:pedido_id>/', views.crear_recibo_multiple, name='crear_recibo_multiple'),
    path('crear-consolidado/<int:pedido_id>/', views.crear_recibo_consolidado, name='crear_recibo_consolidado'),
    path('devolucion/<int:recibo_id>/', views.registrar_devolucion, name='registrar_devolucion'),
    path('devolucion-multiple/<int:pedido_id>/', views.registrar_devolucion_multiple, name='registrar_devolucion_multiple'),
    path('devolucion-consolidado/<int:recibo_id>/', views.registrar_devolucion_consolidado, name='registrar_devolucion_consolidado'),
    path('administrar-productos/<int:recibo_id>/', views.administrar_productos_individuales, name='administrar_productos_individuales'),
    path('pdf/<int:recibo_id>/', views.generar_pdf, name='generar_pdf'),
    path('pdf-consolidado/<int:recibo_id>/', views.generar_pdf_consolidado, name='generar_pdf_consolidado'),
    path('resumen/', views.resumen_sistema, name='resumen_sistema'),
]
