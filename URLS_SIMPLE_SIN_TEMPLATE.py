# urls.py SIMPLE para PythonAnywhere - SIN TEMPLATE PERSONALIZADO
# Copia TODO este contenido y reemplaza completamente tu multiandamios/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

# Vista simple para redireccionar al admin
def redirect_to_admin(request):
    return redirect('/admin/')

# Vista simple para login que redirecciona al admin
def simple_login(request):
    return redirect('/admin/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_admin),  # Página principal redirecciona al admin
    
    # Login simple que redirecciona al admin login
    path('login/', simple_login, name='login'),
    
    # URLs de apps
    path('productos/', include('productos.urls', namespace='productos')),
    # path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    
    # URLs comentadas temporalmente
    # path('', include('usuarios.urls', namespace='usuarios')),
    # path('panel/', include('pedidos.urls', namespace='pedidos')),
    # path('recibos/', include('recibos.urls', namespace='recibos')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
