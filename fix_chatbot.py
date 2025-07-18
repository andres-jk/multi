#!/usr/bin/env python3
"""
Script para solucionar problemas comunes del chatbot
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

def fix_chatbot_issues():
    print("🔧 SOLUCIONANDO PROBLEMAS DEL CHATBOT")
    print("=" * 40)
    
    # 1. Verificar y corregir el archivo JavaScript
    print("\n1. Verificando chatbot.js...")
    
    js_file = 'static/chatbot.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar elementos críticos
        critical_elements = [
            'chatButton',
            'chatWindow', 
            'sendMessage',
            'chatInput',
            'chatMessages'
        ]
        
        missing_elements = []
        for element in critical_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️ Elementos faltantes en JS: {missing_elements}")
        else:
            print("✅ Todos los elementos críticos están en el JS")
    
    # 2. Verificar CSRF en requests
    print("\n2. Verificando configuración CSRF...")
    
    # Buscar configuración CSRF en el JavaScript
    if 'getCookie' in content and 'csrfmiddlewaretoken' in content:
        print("✅ Configuración CSRF correcta")
    else:
        print("⚠️ Posible problema con CSRF token")
    
    # 3. Verificar que el endpoint esté accesible
    print("\n3. Probando endpoint del chatbot...")
    
    from django.test import Client
    import json
    
    client = Client()
    
    # Probar endpoint sin datos
    try:
        response = client.get('/chatbot/api/')
        if response.status_code == 405:  # Method not allowed es esperado para GET
            print("✅ Endpoint responde (405 Method Not Allowed es correcto)")
        else:
            print(f"⚠️ Endpoint respuesta inesperada: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo endpoint: {e}")
    
    # Probar endpoint con datos POST
    try:
        test_data = {"message": "test"}
        response = client.post(
            '/chatbot/api/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            print("✅ Endpoint POST funciona correctamente")
        else:
            print(f"❌ Error en POST: {response.status_code}")
            print(f"   Contenido: {response.content}")
    except Exception as e:
        print(f"❌ Error en test POST: {e}")
    
    # 4. Verificar configuración en settings
    print("\n4. Verificando configuración en settings...")
    
    from django.conf import settings
    
    # Verificar CSRF settings
    csrf_exempt_views = getattr(settings, 'CSRF_EXEMPT_VIEWS', [])
    print(f"   CSRF_EXEMPT_VIEWS: {len(csrf_exempt_views)}")
    
    # Verificar ALLOWED_HOSTS para requests AJAX
    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    print(f"   ALLOWED_HOSTS: {allowed_hosts}")
    
    # 5. Crear una página de prueba del chatbot
    print("\n5. Creando página de prueba...")
    
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Test Chatbot</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>Test del Chatbot</h1>
    <div id="test-area">
        <input type="text" id="testInput" placeholder="Escribe un mensaje de prueba">
        <button onclick="testChatbot()">Probar</button>
        <div id="result"></div>
    </div>
    
    <script>
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    function testChatbot() {
        const message = document.getElementById('testInput').value;
        const resultDiv = document.getElementById('result');
        
        if (!message) {
            alert('Escribe un mensaje');
            return;
        }
        
        resultDiv.innerHTML = 'Enviando...';
        
        fetch('/chatbot/api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            resultDiv.innerHTML = `
                <h3>Respuesta:</h3>
                <p><strong>Status:</strong> ${data.status}</p>
                <p><strong>Mensaje:</strong> ${data.response}</p>
            `;
        })
        .catch(error => {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
            console.error('Error:', error);
        });
    }
    </script>
</body>
</html>'''
    
    # Guardar archivo de prueba
    with open('test_chatbot.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✅ Página de prueba creada: test_chatbot.html")
    
    # 6. Recomendaciones finales
    print("\n" + "=" * 40)
    print("💡 PASOS PARA PROBAR EL CHATBOT:")
    print("1. Abre test_chatbot.html en tu navegador")
    print("2. O usa la consola del navegador en tu sitio (F12)")
    print("3. Verifica errores de JavaScript en la consola")
    print("4. Prueba hacer una petición manual al chatbot")
    
    print("\n🚀 COMANDOS PARA PYTHONANYWHERE:")
    print("cd ~/multi")
    print("python diagnostico_chatbot.py")
    print("python manage.py collectstatic --noinput")
    print("# Luego reload de la aplicación web")
    
    print("\n🔍 SI EL PROBLEMA PERSISTE:")
    print("- Revisa los logs de error de PythonAnywhere")
    print("- Verifica que el JavaScript se carga sin errores")
    print("- Prueba el endpoint directamente: /chatbot/api/")
    print("- Asegúrate de que no hay conflictos de CSS/JS")

if __name__ == "__main__":
    fix_chatbot_issues()
