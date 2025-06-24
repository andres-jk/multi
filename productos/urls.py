from django.urls import path
from . import views

app_name = 'productos'  # Agregando el namespace

urlpatterns = [
    path('', views.catalogo, name='catalogo_productos'),
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
]
