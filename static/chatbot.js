// Chatbot MultiAndamios
console.log('Inicializando chatbot.js');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, inicializando chatbot');
    
    // Dar tiempo a que todo el DOM esté completamente cargado
    setTimeout(() => {
        // Referencias a elementos del DOM
        const chatButton = document.getElementById('chatButton');
        const chatWindow = document.getElementById('chatWindow');
        const closeChat = document.getElementById('closeChat');
        const chatInput = document.getElementById('chatInput');
        const sendMessageButton = document.getElementById('sendMessage');
        const chatMessages = document.getElementById('chatMessages');
        const typingIndicator = document.getElementById('typingIndicator');
        const chatNotification = document.querySelector('.chat-notification');
        const micButton = document.getElementById('micButton');
        
        // Verificar elementos críticos y mostrar en consola
        console.log('Elementos encontrados:', {
            chatButton: !!chatButton,
            chatWindow: !!chatWindow,
            closeChat: !!closeChat,
            chatInput: !!chatInput,
            sendMessageButton: !!sendMessageButton,
            chatMessages: !!chatMessages,
            typingIndicator: !!typingIndicator,
            chatNotification: !!chatNotification,
            micButton: !!micButton
        });
    
    // Inicializar caché de respuestas
    const responseCache = {};
    
    // Tiempo mínimo de respuesta para UX
    const MIN_RESPONSE_TIME = 1000; // milisegundos
    
    // Mostrar/ocultar ventana de chat
    if (chatButton) {
        chatButton.addEventListener('click', function() {
            console.log('Chat button clicked');
            if (chatWindow) {
                chatWindow.classList.toggle('active');
                if (chatWindow.classList.contains('active')) {
                    if (chatInput) chatInput.focus();
                    if (chatNotification) chatNotification.style.display = 'none';
                    chatButton.classList.remove('attention');
                }
            }
        });
    }
    
    // Cerrar chat
    if (closeChat) {
        closeChat.addEventListener('click', function() {
            console.log('Close chat clicked');
            if (chatWindow) chatWindow.classList.remove('active');
        });
    }
    
    // Inicializar botones de respuesta rápida
    initQuickReplyButtons();
    
    // Función para obtener el token CSRF
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
    
    // Inicializar botones de respuesta rápida
    function initQuickReplyButtons() {
        console.log('Inicializando botones de respuesta rápida');
        const buttons = document.querySelectorAll('.quick-reply-btn');
        console.log(`${buttons.length} botones encontrados`);
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                console.log('Quick reply clicked:', this.textContent);
                const query = this.getAttribute('data-query');
                
                // Mostrar mensaje del usuario
                addMessage(query, 'user-message');
                
                // Ocultar botones
                const container = this.closest('.quick-replies');
                if (container) container.style.display = 'none';
                
                // Mostrar indicador de escritura
                if (typingIndicator) typingIndicator.classList.add('active');
                
                // Enviar a la API
                setTimeout(() => {
                    fetchBotResponse(query);
                }, 300);
            });
        });
    }
    
    // Configurar botón de envío
    if (sendMessageButton) {
        console.log('Configurando botón de envío');
        sendMessageButton.addEventListener('click', function() {
            console.log('Send button clicked');
            sendMessage();
        });
    }
    
    // Configurar envío con Enter
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter pressed in input');
                sendMessage();
            }
        });
    }
    
    // Función para enviar mensaje
    function sendMessage() {
        if (!chatInput) return;
        
        const message = chatInput.value.trim();
        if (message === '') return;
        
        console.log('Enviando mensaje:', message);
        
        // Mostrar mensaje del usuario
        addMessage(message, 'user-message');
        chatInput.value = '';
        
        // Mostrar indicador de escritura
        if (typingIndicator) typingIndicator.classList.add('active');
        
        // Verificar caché
        if (responseCache[message.toLowerCase()]) {
            console.log('Respuesta encontrada en caché');
            setTimeout(() => {
                if (typingIndicator) typingIndicator.classList.remove('active');
                const response = responseCache[message.toLowerCase()];
                addMessage(response, 'bot-message');
                generateSuggestions(response);
                scrollToBottom();
            }, MIN_RESPONSE_TIME);
            return;
        }
        
        // Enviar a la API
        fetchBotResponse(message);
    }
    
    // Función para obtener respuesta del bot
    function fetchBotResponse(message) {
        console.log('Solicitando respuesta del bot para:', message);
        const startTime = Date.now();
        
        fetch('/chatbot/api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            console.log('Respuesta recibida del servidor', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Datos de respuesta:', data);
            const elapsedTime = Date.now() - startTime;
            const remainingTime = Math.max(0, MIN_RESPONSE_TIME - elapsedTime);
            
            setTimeout(() => {
                if (typingIndicator) typingIndicator.classList.remove('active');
                
                if (data.status === 'success') {
                    // Guardar en caché
                    responseCache[message.toLowerCase()] = data.response;
                    
                    // Mostrar respuesta
                    addMessage(data.response, 'bot-message');
                    
                    // Mostrar sugerencias
                    generateSuggestions(data.response);
                } else {
                    addMessage('Lo siento, hubo un problema al procesar tu solicitud.', 'bot-message');
                }
                
                scrollToBottom();
            }, remainingTime);
        })
        .catch(error => {
            console.error('Error en chatbot API:', error);
            const elapsedTime = Date.now() - startTime;
            const remainingTime = Math.max(0, MIN_RESPONSE_TIME - elapsedTime);
            
            setTimeout(() => {
                if (typingIndicator) typingIndicator.classList.remove('active');
                addMessage('Lo siento, no pude conectarme al servicio de chat.', 'bot-message');
                scrollToBottom();
            }, remainingTime);
        });
    }
    
    // Función para analizar y generar sugerencias
    function generateSuggestions(response) {
        console.log('Generando sugerencias basadas en:', response.substring(0, 50) + '...');
        const responseLower = response.toLowerCase();
        let suggestions = [];
        
        if (responseLower.includes('andamio')) {
            suggestions = ['¿Cuáles son los precios?', '¿Son seguros los andamios?', '¿Cómo alquilo un andamio?'];
        } else if (responseLower.includes('formaleta')) {
            suggestions = ['¿Qué tipos de formaletas tienen?', '¿Cuál es el precio?', '¿Cómo se instalan?'];
        } else if (responseLower.includes('precio')) {
            suggestions = ['¿Hay descuentos por volumen?', 'Quiero una cotización personalizada', '¿Cuáles son las formas de pago?'];
        } else if (responseLower.includes('alquiler')) {
            suggestions = ['¿Qué documentos necesito?', '¿Puedo extender el periodo?', '¿Cómo hago la devolución?'];
        } else if (responseLower.includes('entrega')) {
            suggestions = ['¿Cuál es el costo de entrega?', '¿Entregan fuera de la ciudad?', '¿Cuánto tiempo tarda?'];
        } else {
            suggestions = ['Quiero conocer más sobre andamios', '¿Tienen formaletas disponibles?', '¿Cómo es el proceso de alquiler?'];
        }
        
        showSuggestions(suggestions);
    }
    
    // Función para mostrar sugerencias
    function showSuggestions(suggestions) {
        console.log('Mostrando sugerencias:', suggestions);
        
        // Crear contenedor
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'quick-replies';
        
        // Crear botones
        suggestions.forEach(suggestion => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.textContent = suggestion;
            button.setAttribute('data-query', suggestion);
            
            button.addEventListener('click', function() {
                console.log('Sugerencia seleccionada:', this.textContent);
                const query = this.getAttribute('data-query');
                
                // Mostrar mensaje del usuario
                addMessage(query, 'user-message');
                
                // Ocultar botones de sugerencias
                const allReplies = document.querySelectorAll('.quick-replies');
                allReplies.forEach(r => r.style.display = 'none');
                
                // Mostrar indicador de escritura
                if (typingIndicator) typingIndicator.classList.add('active');
                
                // Enviar a la API
                setTimeout(() => {
                    fetchBotResponse(query);
                }, 300);
            });
            
            suggestionsDiv.appendChild(button);
        });
        
        // Agregar al chat
        if (chatMessages) {
            chatMessages.appendChild(suggestionsDiv);
            scrollToBottom();
        }
    }
    
    // Función para agregar mensajes
    function addMessage(text, className) {
        if (!chatMessages) return;
        console.log('Agregando mensaje:', className, text.substring(0, 30) + '...');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.innerHTML = formatMessageText(text);
        
        // Agregar botones de reacción para mensajes del bot
        if (className === 'bot-message') {
            const reactionsDiv = document.createElement('div');
            reactionsDiv.className = 'message-reactions';
            
            const likeButton = document.createElement('button');
            likeButton.className = 'reaction-btn';
            likeButton.setAttribute('data-reaction', 'like');
            likeButton.innerHTML = '<i class="fas fa-thumbs-up"></i>';
            
            const dislikeButton = document.createElement('button');
            dislikeButton.className = 'reaction-btn';
            dislikeButton.setAttribute('data-reaction', 'dislike');
            dislikeButton.innerHTML = '<i class="fas fa-thumbs-down"></i>';
            
            reactionsDiv.appendChild(likeButton);
            reactionsDiv.appendChild(dislikeButton);
            messageDiv.appendChild(reactionsDiv);
            
            // Inicializar botones de reacción
            [likeButton, dislikeButton].forEach(btn => {
                btn.addEventListener('click', function() {
                    console.log('Reacción:', this.getAttribute('data-reaction'));
                    reactionsDiv.querySelectorAll('.reaction-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                });
            });
        }
        
        // Animación de entrada
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        chatMessages.appendChild(messageDiv);
        
        // Forzar reflow y animar
        messageDiv.offsetHeight;
        messageDiv.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
        
        scrollToBottom();
    }
    
    // Función para formatear texto de mensajes
    function formatMessageText(text) {
        // Enlaces clicables
        text = text.replace(/https?:\/\/[^\s]+/g, match => {
            return `<a href="${match}" target="_blank" rel="noopener noreferrer">${match}</a>`;
        });
        
        // Saltos de línea
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    // Función para hacer scroll al final
    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
      // Función para inicializar botones de reacción
    function initReactionButtons() {
        console.log('Inicializando botones de reacción');
        const buttons = document.querySelectorAll('.reaction-btn');
        
        buttons.forEach(button => {
            if (!button.hasListener) {
                button.addEventListener('click', function() {
                    const reaction = this.getAttribute('data-reaction');
                    console.log('Reacción registrada:', reaction);
                    
                    // Marcar como activo y desactivar el otro botón
                    const parent = this.closest('.message-reactions');
                    if (parent) {
                        const allButtons = parent.querySelectorAll('.reaction-btn');
                        allButtons.forEach(btn => btn.classList.remove('active'));
                        this.classList.add('active');
                    }
                });
                button.hasListener = true;
            }
        });
    }
    
    // Inicializar los botones de reacción existentes
    initReactionButtons();
    
    // Simulación de actividad después de unos segundos
    setTimeout(() => {
        if (chatButton && chatNotification && chatWindow && !chatWindow.classList.contains('active')) {
            chatNotification.classList.add('bounce');
            chatButton.classList.add('attention');
        }
    }, 15000);
      console.log('Inicialización de chatbot completada');
    }, 100); // Cerramos el setTimeout que agregamos para dar tiempo al DOM
});
