// Chatbot MultiAndamios - Versión Corregida
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
            messageDiv.innerHTML = message.replace(/\n/g, '<br>');
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

console.log('🤖 Chatbot script cargado completamente');