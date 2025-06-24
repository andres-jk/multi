from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/', views.chat_api, name='chat_api'),
    path('', views.chat_view, name='chat_view'),
]
