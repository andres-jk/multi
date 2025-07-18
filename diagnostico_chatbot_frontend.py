#!/usr/bin/env python3
"""
Script de diagnóstico avanzado para problemas del chatbot frontend
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

def diagnosticar_frontend_chatbot():
    print("🔍 DIAGNÓSTICO FRONTEND DEL CHATBOT")
    print("=" * 45)
    
    # 1. Verificar archivos estáticos
    print("\n1. Verificando archivos estáticos...")
    
    static_files = {
        'static/chatbot.js': 'JavaScript del chatbot',
        'templates/base.html': 'Template principal',
        'usuarios/templates/base.html': 'Template usuarios'
    }
    
    for file_path, desc in static_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {desc}: {file_path} ({size} bytes)")
        else:
            print(f"❌ {desc}: {file_path} NO ENCONTRADO")
    
    # 2. Verificar contenido del JavaScript
    print("\n2. Analizando chatbot.js...")
    
    js_file = 'static/chatbot.js'
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos críticos
        checks = {
            'DOMContentLoaded': 'Event listener principal',
            'getElementById': 'Búsqueda de elementos DOM',
            'chatButton': 'Referencia al botón del chat',
            'chatWindow': 'Referencia a la ventana del chat',
            'addEventListener': 'Event listeners',
            'function getCookie': 'Función CSRF',
            'fetch(': 'Llamadas AJAX',
            '/chatbot/api/': 'Endpoint del chatbot'
        }
        
        for check, desc in checks.items():
            if check in content:
                print(f"✅ {desc}: Presente")
            else:
                print(f"❌ {desc}: FALTANTE")
        
        # Verificar errores de sintaxis básicos
        if content.count('{') != content.count('}'):
            print("⚠️ Posible error de sintaxis: llaves desbalanceadas")
        
        if content.count('(') != content.count(')'):
            print("⚠️ Posible error de sintaxis: paréntesis desbalanceados")
    
    # 3. Verificar integración en templates
    print("\n3. Verificando integración en templates...")
    
    templates_to_check = [
        'templates/base.html',
        'usuarios/templates/base.html'
    ]
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n📄 {template_path}:")
            
            # Verificar elementos del chatbot
            elements = {
                'id="chatButton"': 'Botón del chatbot',
                'id="chatWindow"': 'Ventana del chatbot',
                'chatbot.js': 'Script del chatbot',
                'chat-bot-button': 'Clase CSS del botón',
                'chat-bot-window': 'Clase CSS de la ventana'
            }
            
            for element, desc in elements.items():
                if element in content:
                    print(f"  ✅ {desc}")
                else:
                    print(f"  ❌ {desc} FALTANTE")
    
    # 4. Crear test HTML independiente
    print("\n4. Creando test HTML independiente...")
    
    test_html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Chatbot Frontend</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        
        /* Estilos del chatbot copiados */
        .chat-bot-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #F9C552, #e6b143);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(249, 197, 82, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
            animation: pulse 2s infinite;
        }
        
        .chat-bot-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(249, 197, 82, 0.6);
        }
        
        .chat-bot-button i {
            color: #1A1228;
            font-size: 24px;
        }
        
        .chat-notification {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #FF99BA;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(249, 197, 82, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(249, 197, 82, 0); }
            100% { box-shadow: 0 0 0 0 rgba(249, 197, 82, 0); }
        }
        
        .chat-bot-window {
            position: fixed;
            bottom: 100px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            z-index: 999;
            transform: translateY(20px);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .chat-bot-window.active {
            transform: translateY(0);
            opacity: 1;
            visibility: visible;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <h1>🤖 Test Frontend del Chatbot</h1>
    
    <div id="status"></div>
    
    <h2>Elementos del Chatbot:</h2>
    
    <!-- Botón del chatbot -->
    <div class="chat-bot-button" id="chatButton">
        <i class="fas fa-comment-dots"></i>
        <span class="chat-notification">1</span>
    </div>
    
    <!-- Ventana del chatbot -->
    <div class="chat-bot-window" id="chatWindow">
        <div style="padding: 20px;">
            <h3>Chat Test</h3>
            <p>Esta es una ventana de prueba del chatbot.</p>
            <button onclick="testChatAPI()">Probar API</button>
            <div id="apiResult" style="margin-top: 10px;"></div>
        </div>
    </div>
    
    <h2>Tests:</h2>
    <button onclick="runTests()">Ejecutar Tests</button>
    <div id="testResults"></div>
    
    <script>
        // Función CSRF
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
        
        // Test de elementos DOM
        function runTests() {
            const results = document.getElementById('testResults');
            results.innerHTML = '<h3>Resultados de Tests:</h3>';
            
            const tests = [
                { name: 'Botón del chatbot', element: 'chatButton' },
                { name: 'Ventana del chatbot', element: 'chatWindow' },
                { name: 'Font Awesome', test: () => document.querySelector('link[href*="font-awesome"]') !== null },
                { name: 'JavaScript funcionando', test: () => true }
            ];
            
            tests.forEach(test => {
                let passed = false;
                
                if (test.element) {
                    const element = document.getElementById(test.element);
                    passed = element !== null && element.style.display !== 'none';
                    
                    if (passed) {
                        results.innerHTML += `<div class="status success">✅ ${test.name}: Elemento encontrado</div>`;
                    } else {
                        results.innerHTML += `<div class="status error">❌ ${test.name}: Elemento no encontrado</div>`;
                    }
                } else if (test.test) {
                    passed = test.test();
                    const status = passed ? 'success' : 'error';
                    const icon = passed ? '✅' : '❌';
                    results.innerHTML += `<div class="status ${status}">${icon} ${test.name}: ${passed ? 'OK' : 'FALLO'}</div>`;
                }
            });
        }
        
        // Test de API
        function testChatAPI() {
            const resultDiv = document.getElementById('apiResult');
            resultDiv.innerHTML = 'Probando API...';
            
            fetch('/chatbot/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: 'test frontend' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    resultDiv.innerHTML = '<div class="status success">✅ API funcionando: ' + data.response.substring(0, 50) + '...</div>';
                } else {
                    resultDiv.innerHTML = '<div class="status error">❌ Error API: ' + data.status + '</div>';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div class="status error">❌ Error de red: ' + error.message + '</div>';
            });
        }
        
        // Event listeners
        document.addEventListener('DOMContentLoaded', function() {
            const chatButton = document.getElementById('chatButton');
            const chatWindow = document.getElementById('chatWindow');
            
            if (chatButton) {
                chatButton.addEventListener('click', function() {
                    console.log('Botón del chat clickeado');
                    if (chatWindow) {
                        chatWindow.classList.toggle('active');
                    }
                });
                
                document.getElementById('status').innerHTML = 
                    '<div class="status success">✅ Chat button listener configurado</div>';
            } else {
                document.getElementById('status').innerHTML = 
                    '<div class="status error">❌ No se pudo configurar el chat button</div>';
            }
            
            // Auto-ejecutar tests
            setTimeout(runTests, 500);
        });
    </script>
</body>
</html>'''
    
    with open('test_chatbot_frontend.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✅ Test frontend creado: test_chatbot_frontend.html")
    
    # 5. Crear versión corregida del chatbot.js
    print("\n5. Creando versión corregida de chatbot.js...")
    
    js_corregido = '''// Chatbot MultiAndamios - Versión Corregida
console.log('🤖 Inicializando chatbot.js v2.0');

document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM cargado, configurando chatbot...');
    
    // Función para obtener CSRF token
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
    
    // Dar tiempo para que el DOM esté completamente cargado
    setTimeout(() => {
        // Referencias a elementos del DOM
        const chatButton = document.getElementById('chatButton');
        const chatWindow = document.getElementById('chatWindow');
        const closeChat = document.getElementById('closeChat');
        const chatInput = document.getElementById('chatInput');
        const sendMessageButton = document.getElementById('sendMessage');
        const chatMessages = document.getElementById('chatMessages');
        const typingIndicator = document.getElementById('typingIndicator');
        
        console.log('🔍 Elementos encontrados:', {
            chatButton: !!chatButton,
            chatWindow: !!chatWindow,
            closeChat: !!closeChat,
            chatInput: !!chatInput,
            sendMessageButton: !!sendMessageButton,
            chatMessages: !!chatMessages,
            typingIndicator: !!typingIndicator
        });
        
        // Verificar que al menos el botón existe
        if (!chatButton) {
            console.error('❌ No se encontró el botón del chatbot (ID: chatButton)');
            return;
        }
        
        // Configurar el botón del chatbot
        chatButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🖱️ Botón del chatbot clickeado');
            
            if (chatWindow) {
                chatWindow.classList.toggle('active');
                console.log('💬 Ventana del chat toggled:', chatWindow.classList.contains('active'));
                
                if (chatWindow.classList.contains('active')) {
                    if (chatInput) chatInput.focus();
                    // Ocultar notificación si existe
                    const notification = chatButton.querySelector('.chat-notification');
                    if (notification) notification.style.display = 'none';
                    chatButton.classList.remove('attention');
                }
            } else {
                console.warn('⚠️ No se encontró la ventana del chat (ID: chatWindow)');
                // Crear ventana de emergencia
                createEmergencyChatWindow();
            }
        });
        
        // Configurar el botón de cerrar
        if (closeChat) {
            closeChat.addEventListener('click', function() {
                console.log('❌ Cerrando chat');
                if (chatWindow) chatWindow.classList.remove('active');
            });
        }
        
        // Configurar envío de mensajes
        if (sendMessageButton && chatInput) {
            sendMessageButton.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
        
        // Función para enviar mensaje
        function sendMessage() {
            if (!chatInput) {
                console.error('❌ No se encontró el input del chat');
                return;
            }
            
            const message = chatInput.value.trim();
            if (!message) return;
            
            console.log('📤 Enviando mensaje:', message);
            
            // Añadir mensaje del usuario
            addMessage(message, 'user-message');
            chatInput.value = '';
            
            // Mostrar indicador de escritura
            if (typingIndicator) typingIndicator.classList.add('active');
            
            // Enviar a la API
            fetch('/chatbot/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => {
                console.log('📥 Respuesta recibida:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('💬 Datos del chatbot:', data);
                
                // Ocultar indicador de escritura
                if (typingIndicator) typingIndicator.classList.remove('active');
                
                if (data.status === 'success') {
                    addMessage(data.response, 'bot-message');
                } else {
                    addMessage('Lo siento, hubo un problema. Intenta de nuevo.', 'bot-message');
                }
                
                scrollToBottom();
            })
            .catch(error => {
                console.error('❌ Error en API:', error);
                
                // Ocultar indicador de escritura
                if (typingIndicator) typingIndicator.classList.remove('active');
                
                addMessage('Error de conexión. Por favor intenta más tarde.', 'bot-message');
                scrollToBottom();
            });
        }
        
        // Función para añadir mensaje
        function addMessage(message, className) {
            if (!chatMessages) {
                console.warn('⚠️ No se encontró el contenedor de mensajes');
                return;
            }
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${className}`;
            messageDiv.innerHTML = message.replace(/\\n/g, '<br>');
            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        }
        
        // Función para scroll automático
        function scrollToBottom() {
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
        
        // Crear ventana de emergencia si no existe
        function createEmergencyChatWindow() {
            console.log('🚨 Creando ventana de chat de emergencia');
            
            const emergencyWindow = document.createElement('div');
            emergencyWindow.id = 'chatWindow';
            emergencyWindow.className = 'chat-bot-window active';
            emergencyWindow.innerHTML = `
                <div style="padding: 20px; text-align: center;">
                    <h3>Chat MultiAndamios</h3>
                    <p>El chat está en modo de emergencia.</p>
                    <p>Contacta con nosotros:</p>
                    <p>📞 Teléfono: +57 (1) 234-5678</p>
                    <p>📧 Email: info@multiandamios.com</p>
                    <button onclick="this.parentElement.parentElement.remove()">Cerrar</button>
                </div>
            `;
            document.body.appendChild(emergencyWindow);
        }
        
        // Mensaje de inicialización exitosa
        console.log('✅ Chatbot inicializado correctamente');
        
        // Auto-test después de 2 segundos
        setTimeout(() => {
            if (chatButton && chatButton.offsetWidth > 0 && chatButton.offsetHeight > 0) {
                console.log('✅ Botón del chatbot visible y funcional');
            } else {
                console.error('❌ Botón del chatbot no es visible');
            }
        }, 2000);
        
    }, 100); // Delay de 100ms para asegurar carga completa
});

// Test global para debugging
window.testChatbot = function() {
    const button = document.getElementById('chatButton');
    if (button) {
        button.click();
        console.log('🧪 Test del chatbot ejecutado');
    } else {
        console.error('🧪 Test falló: botón no encontrado');
    }
};

console.log('🤖 Chatbot script cargado completamente');'''
    
    with open('static/chatbot_corregido.js', 'w', encoding='utf-8') as f:
        f.write(js_corregido)
    
    print("✅ Versión corregida creada: static/chatbot_corregido.js")
    
    # 6. Instrucciones finales
    print("\n" + "=" * 45)
    print("🎯 PASOS PARA SOLUCIONAR:")
    print("1. Abre test_chatbot_frontend.html en tu navegador")
    print("2. Revisa qué elementos faltan o no funcionan")
    print("3. Reemplaza chatbot.js con chatbot_corregido.js si es necesario")
    print("4. Verifica la consola del navegador (F12) para errores")
    print("5. Asegúrate de que Font Awesome se esté cargando")
    
    print("\n🔧 COMANDOS PARA PYTHONANYWHERE:")
    print("cp static/chatbot_corregido.js static/chatbot.js")
    print("python manage.py collectstatic --noinput")
    print("# Reiniciar aplicación web")
    
    print("\n🆘 SI EL PROBLEMA PERSISTE:")
    print("- El template base.html podría tener problemas")
    print("- Posible conflicto con CSS/JS")
    print("- Error en la estructura HTML")
    print("- Problemas de caché del navegador")

if __name__ == "__main__":
    diagnosticar_frontend_chatbot()
