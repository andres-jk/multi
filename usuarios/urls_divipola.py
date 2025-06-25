from django.urls import path
from . import views_divipola

urlpatterns = [
    # ... tus otras URLs existentes ...
    
    # URLs para DIVIPOLA
    path('api/departamentos/', views_divipola.get_departamentos, name='get_departamentos'),
    path('api/municipios/', views_divipola.get_municipios, name='get_municipios'),
]
