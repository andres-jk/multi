#!/usr/bin/env python3
"""
Script de diagnóstico para el chatbot de MultiAndamios
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from chatbot.views import get_ai_response, chat_api

def diagnosticar_chatbot():
    print("🤖 DIAGNÓSTICO DEL CHATBOT MULTIANDAMIOS")
    print("=" * 50)
    
    # 1. Verificar que la app chatbot esté instalada
    from django.conf import settings
    if 'chatbot' in settings.INSTALLED_APPS:
        print("✅ App 'chatbot' está instalada")
    else:
        print("❌ App 'chatbot' NO está instalada")
        return
    
    # 2. Verificar URLs
    print("\n📍 Verificando URLs...")
    try:
        from django.urls import reverse
        chat_api_url = reverse('chatbot:chat_api')
        chat_view_url = reverse('chatbot:chat_view')
        print(f"✅ URL chat_api: {chat_api_url}")
        print(f"✅ URL chat_view: {chat_view_url}")
    except Exception as e:
        print(f"❌ Error en URLs: {e}")
    
    # 3. Probar la función get_ai_response
    print("\n🧠 Probando función get_ai_response...")
    test_queries = [
        "hola",
        "andamios disponibles",
        "precios de formaletas",
        "contacto",
        "gracias"
    ]
    
    for query in test_queries:
        try:
            response = get_ai_response(query, "test_user")
            print(f"✅ Query: '{query}' -> Respuesta: {response[:50]}...")
        except Exception as e:
            print(f"❌ Error con query '{query}': {e}")
    
    # 4. Probar la vista API con cliente de prueba
    print("\n🌐 Probando vista API...")
    client = Client()
    
    test_data = {
        "message": "¿Qué tipos de andamios tienen disponibles?"
    }
    
    try:
        response = client.post(
            '/chatbot/api/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API responde correctamente")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Respuesta: {data.get('response', 'N/A')[:100]}...")
        else:
            print(f"❌ API error - Status: {response.status_code}")
            print(f"   Contenido: {response.content}")
            
    except Exception as e:
        print(f"❌ Error probando API: {e}")
    
    # 5. Verificar archivos estáticos
    print("\n📁 Verificando archivos estáticos...")
    static_files = [
        'static/chatbot.js',
        'chatbot/templates/chatbot/chat.html'
    ]
    
    for file_path in static_files:
        full_path = os.path.join('.', file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} existe")
        else:
            print(f"❌ {file_path} NO existe")
    
    # 6. Verificar la base de conocimientos
    print("\n📚 Verificando base de conocimientos...")
    try:
        from chatbot.knowledge_base import PRODUCTOS, SERVICIOS, CONTACTO
        print(f"✅ PRODUCTOS: {len(PRODUCTOS)} categorías")
        print(f"✅ SERVICIOS: {len(SERVICIOS)} categorías")
        print(f"✅ CONTACTO: {len(CONTACTO)} campos")
    except Exception as e:
        print(f"❌ Error en base de conocimientos: {e}")
    
    # 7. Verificar integración en templates
    print("\n🎨 Verificando integración en templates...")
    template_files = [
        'templates/base.html',
        'usuarios/templates/base.html'
    ]
    
    for template in template_files:
        full_path = os.path.join('.', template)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'chatButton' in content and 'chatWindow' in content:
                    print(f"✅ {template} tiene elementos del chatbot")
                else:
                    print(f"⚠️ {template} existe pero falta integración del chatbot")
        else:
            print(f"❌ {template} NO existe")
    
    print("\n" + "=" * 50)
    print("🔍 RESUMEN DEL DIAGNÓSTICO")
    print("Si ves errores arriba, revisa:")
    print("1. ¿Está 'chatbot' en INSTALLED_APPS?")
    print("2. ¿Están las URLs configuradas correctamente?")
    print("3. ¿Existe el archivo static/chatbot.js?")
    print("4. ¿Está el botón del chatbot en el template base?")
    print("5. ¿Hay errores de JavaScript en la consola del navegador?")
    
    # 8. Sugerencias para solucionar problemas comunes
    print("\n💡 POSIBLES SOLUCIONES:")
    print("- Si el botón no aparece: Verificar que chatbot.js se carga")
    print("- Si no responde: Revisar consola del navegador (F12)")
    print("- Si hay error 404: Verificar configuración de URLs")
    print("- Si respuestas vacías: Verificar knowledge_base.py")

if __name__ == "__main__":
    diagnosticar_chatbot()
