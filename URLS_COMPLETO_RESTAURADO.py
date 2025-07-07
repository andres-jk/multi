# urls.py COMPLETO RESTAURADO para PythonAnywhere
# Copia TODO este contenido y reemplaza completamente tu multiandamios/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls', namespace='usuarios')),  # PÁGINA PRINCIPAL
    path('productos/', include('productos.urls', namespace='productos')),
    path('panel/', include('pedidos.urls', namespace='pedidos')),
    path('recibos/', include('recibos.urls', namespace='recibos')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
