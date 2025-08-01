#!/bin/bash

# 📁 TEMPLATE COMPLETO CORREGIDO PARA PYTHONANYWHERE
# Ejecutar: bash subir_template_corregido.sh

echo "📤 SUBIENDO TEMPLATE GPS CORREGIDO A PYTHONANYWHERE..."

# Crear el archivo completo corregido
cat > template_seguimiento_cliente_corregido.html << 'TEMPLATE_EOF'
{% extends 'base.html' %}
{% load humanize %}

{% block title %}Seguimiento de Mi Pedido #{{ pedido.id_pedido }} - MultiAndamios{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
.tracking-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
}

.tracking-header h1,
.tracking-header h2,
.tracking-header p {
    color: white;
}

.status-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    border: 2px solid #e9ecef;
    color: #212529;
}

.status-card h3,
.status-card h4,
.status-card h5,
.status-card strong {
    color: #343a40;
}

.status-card .text-muted {
    color: #6c757d !important;
}

.status-card.active {
    border-color: #28a745;
    background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
    color: #155724;
}

.status-card.current {
    border-color: #ffc107;
    background: linear-gradient(135deg, #fffbf0 0%, #fff8e1 100%);
    animation: glow 2s ease-in-out infinite alternate;
    color: #856404;
}

@keyframes glow {
    from { box-shadow: 0 5px 15px rgba(255, 193, 7, 0.2); }
    to { box-shadow: 0 5px 25px rgba(255, 193, 7, 0.4); }
}

.map-container {
    height: 400px;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.delivery-info {
    background: #f8f9fa;
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 20px;
    color: #212529;
}

.delivery-info h3,
.delivery-info h4,
.delivery-info h5,
.delivery-info strong {
    color: #343a40;
}

.delivery-info .text-muted {
    color: #6c757d !important;
}

.info-item {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    padding: 15px;
    background: white;
    border-radius: 10px;
    border-left: 4px solid #007bff;
    color: #212529;
}

.info-item strong {
    color: #343a40;
}

.info-item:last-child {
    margin-bottom: 0;
}

.info-item .icon {
    font-size: 1.5rem;
    margin-right: 15px;
    color: #007bff;
}

.timeline {
    position: relative;
    padding: 20px 0;
    color: #212529;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 30px;
    top: 0;
    height: 100%;
    width: 3px;
    background: #dee2e6;
}

.timeline-step {
    position: relative;
    padding: 20px 0 20px 80px;
    margin-bottom: 20px;
}

.timeline-step::before {
    content: '';
    position: absolute;
    left: 19px;
    top: 30px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 3px solid #dee2e6;
    background: white;
}

.timeline-step.completed::before {
    border-color: #28a745;
    background: #28a745;
}

.timeline-step.current::before {
    border-color: #ffc107;
    background: #ffc107;
    animation: pulse 2s infinite;
}

.timeline-step.pending::before {
    border-color: #dee2e6;
    background: white;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.vehicle-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    border: 2px solid #2196f3;
}

.eta-card {
    background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    border: 2px solid #ff9800;
}

.contact-card {
    background: linear-gradient(135deg, #e8f5e8 0%, #4caf50 100%);
    color: white;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}

.btn-call {
    background: #4caf50;
    border: none;
    color: white;
    padding: 12px 30px;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-call:hover {
    background: #45a049;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
}

.refresh-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,123,255,0.4);
    transition: all 0.3s ease;
}

.refresh-button:hover {
    transform: scale(1.1);
    background: #0056b3;
}

.live-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    background: #ff4444;
    border-radius: 50%;
    animation: blink 1s linear infinite;
    margin-right: 8px;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
</style>
{% endblock %}

{% block content %}
<div class="container">
    <!-- Encabezado -->
    <div class="tracking-header">
        <h1 class="h2 mb-3">
            <i class="fas fa-truck"></i>
            Seguimiento de Mi Pedido #{{ pedido.id_pedido }}
        </h1>
        <div class="row">
            <div class="col-md-4">
                <h5>Estado Actual</h5>
                <p class="h4">{{ entrega.get_estado_entrega_display }}</p>
            </div>
            <div class="col-md-4">
                <h5>Valor del Pedido</h5>
                <p class="h4">${{ pedido.total|floatformat:0|intcomma }}</p>
            </div>
            <div class="col-md-4">
                <h5>Fecha de Entrega</h5>
                <p class="h4">{{ entrega.fecha_programada|date:"d/m/Y" }}</p>
            </div>
        </div>
    </div>

    <!-- Timeline de Estados -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="status-card">
                <h4 class="mb-4"><i class="fas fa-route text-primary"></i> Progreso de la Entrega</h4>
                <div class="timeline">
                    <div class="timeline-step completed">
                        <div class="timeline-content">
                            <h5>Pedido Confirmado</h5>
                            <p class="text-muted mb-0">Tu pedido ha sido confirmado y está siendo preparado</p>
                            <small class="text-success">✓ Completado</small>
                        </div>
                    </div>
                    
                    <div class="timeline-step {% if entrega.fecha_inicio_recorrido %}completed{% elif entrega.estado_entrega == 'programada' %}current{% else %}pending{% endif %}">
                        <div class="timeline-content">
                            <h5>Entrega Programada</h5>
                            <p class="text-muted mb-1">Fecha programada: {{ entrega.fecha_programada|date:"d/m/Y H:i" }}</p>
                            {% if entrega.estado_entrega == 'programada' %}
                            <small class="text-warning">📅 Programada</small>
                            {% else %}
                            <small class="text-success">✓ Completado</small>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="timeline-step {% if entrega.estado_entrega == 'en_camino' %}current{% elif entrega.estado_entrega == 'entregada' %}completed{% else %}pending{% endif %}">
                        <div class="timeline-content">
                            <h5>En Camino</h5>
                            {% if entrega.estado_entrega == 'en_camino' %}
                            <p class="text-warning mb-1">
                                <span class="live-indicator"></span>
                                El vehículo está en camino hacia tu dirección
                            </p>
                            {% if entrega.fecha_inicio_recorrido %}
                            <small class="text-muted">Iniciado: {{ entrega.fecha_inicio_recorrido|date:"H:i" }}</small>
                            {% endif %}
                            {% elif entrega.estado_entrega == 'entregada' %}
                            <p class="text-muted mb-0">El vehículo llegó a tu dirección</p>
                            <small class="text-success">✓ Completado</small>
                            {% else %}
                            <p class="text-muted mb-0">El vehículo iniciará el recorrido pronto</p>
                            <small class="text-secondary">⏳ Pendiente</small>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="timeline-step {% if entrega.estado_entrega == 'entregada' %}completed{% else %}pending{% endif %}">
                        <div class="timeline-content">
                            <h5>Entrega Completada</h5>
                            {% if entrega.estado_entrega == 'entregada' %}
                            <p class="text-muted mb-1">Tu pedido fue entregado exitosamente</p>
                            <small class="text-success">✓ Entregado el {{ entrega.fecha_entrega_real|date:"d/m/Y H:i" }}</small>
                            {% else %}
                            <p class="text-muted mb-0">Tu pedido será entregado en tu dirección</p>
                            <small class="text-secondary">⏳ Pendiente</small>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Información del Vehículo y Conductor -->
    <div class="row mb-4">
        <div class="col-md-4">
            <div class="vehicle-card">
                <i class="fas fa-truck fa-3x mb-3 text-primary"></i>
                <h5>Vehículo</h5>
                <p class="h4 mb-0">{{ entrega.vehiculo_placa }}</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="contact-card">
                <i class="fas fa-user-tie fa-3x mb-3"></i>
                <h5>Conductor</h5>
                <p class="h5 mb-2">{{ entrega.conductor_nombre }}</p>
                <button class="btn btn-call" onclick="llamarConductor()">
                    <i class="fas fa-phone"></i> {{ entrega.conductor_telefono }}
                </button>
            </div>
        </div>
        <div class="col-md-4">
            {% if entrega.tiempo_estimado_llegada and entrega.estado_entrega == 'en_camino' %}
            <div class="eta-card">
                <i class="fas fa-clock fa-3x mb-3 text-warning"></i>
                <h5>Tiempo Estimado</h5>
                <p class="h4 mb-0" id="eta-countdown">{{ entrega.tiempo_estimado_llegada|date:"H:i" }}</p>
            </div>
            {% else %}
            <div class="delivery-info">
                <i class="fas fa-map-marker-alt fa-3x mb-3 text-info"></i>
                <h5>Dirección de Entrega</h5>
                <p class="mb-0">{{ pedido.direccion_entrega }}</p>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Mapa en Tiempo Real -->
    {% if entrega.estado_entrega == 'en_camino' and puede_ver_ubicacion %}
    <div class="row mb-4">
        <div class="col-12">
            <div class="status-card current">
                <h4 class="mb-3">
                    <span class="live-indicator"></span>
                    <i class="fas fa-map-marked-alt text-warning"></i>
                    Ubicación en Tiempo Real
                </h4>
                <div id="map" class="map-container"></div>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="info-item">
                            <div class="icon"><i class="fas fa-clock"></i></div>
                            <div>
                                <strong>Última actualización:</strong><br>
                                <span id="ultima-actualizacion">{{ entrega.ultima_actualizacion_gps|date:"H:i:s"|default:"No disponible" }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        {% if entrega.distancia_restante_km %}
                        <div class="info-item">
                            <div class="icon"><i class="fas fa-route"></i></div>
                            <div>
                                <strong>Distancia restante:</strong><br>
                                <span id="distancia-restante">{{ entrega.distancia_restante_km }} km</span>
                            </div>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <!-- Información Adicional -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="delivery-info">
                <h5><i class="fas fa-info-circle text-primary"></i> Información del Pedido</h5>
                <div class="info-item">
                    <div class="icon"><i class="fas fa-calendar"></i></div>
                    <div>
                        <strong>Fecha de pedido:</strong><br>
                        {{ pedido.fecha|date:"d/m/Y H:i" }}
                    </div>
                </div>
                <div class="info-item">
                    <div class="icon"><i class="fas fa-clock"></i></div>
                    <div>
                        <strong>Duración de renta:</strong><br>
                        {{ pedido.duracion_renta }} días
                    </div>
                </div>
                {% if entrega.estado_entrega == 'entregada' %}
                <div class="info-item">
                    <div class="icon"><i class="fas fa-undo"></i></div>
                    <div>
                        <strong>Fecha límite devolución:</strong><br>
                        {{ pedido.get_fecha_limite_devolucion|date:"d/m/Y H:i" }}
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="delivery-info">
                <h5><i class="fas fa-headset text-primary"></i> ¿Necesitas Ayuda?</h5>
                <div class="info-item">
                    <div class="icon"><i class="fas fa-phone"></i></div>
                    <div>
                        <strong>Línea de atención:</strong><br>
                        <a href="tel:+573001234567" class="text-decoration-none">+57 300 123 4567</a>
                    </div>
                </div>
                <div class="info-item">
                    <div class="icon"><i class="fas fa-envelope"></i></div>
                    <div>
                        <strong>Email de soporte:</strong><br>
                        <a href="mailto:soporte@multiandamios.com" class="text-decoration-none">soporte@multiandamios.com</a>
                    </div>
                </div>
                <div class="info-item">
                    <div class="icon"><i class="fas fa-comments"></i></div>
                    <div>
                        <strong>Chat en línea:</strong><br>
                        <button class="btn btn-sm btn-primary">Iniciar Chat</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Botón de actualización -->
<button class="refresh-button" onclick="actualizarDatos()" title="Actualizar datos">
    <i class="fas fa-sync-alt"></i>
</button>

<!-- Scripts -->
<script>
let map;
let vehicleMarker;
let destinationMarker;

// Datos de la entrega
const pedidoId = {{ pedido.id_pedido }};
const estadoEntrega = '{{ entrega.estado_entrega }}';

{% if entrega.estado_entrega == 'en_camino' and puede_ver_ubicacion %}
// Inicializar mapa con OpenStreetMap
function initMap() {
    // Coordenadas por defecto (Bogotá)
    let defaultLat = 4.7110;
    let defaultLng = -74.0721;
    
    // Si hay coordenadas guardadas, usarlas
    {% if entrega.latitud_actual and entrega.longitud_actual %}
    defaultLat = {{ entrega.latitud_actual }};
    defaultLng = {{ entrega.longitud_actual }};
    {% endif %}
    
    // Crear mapa
    map = L.map('map').setView([defaultLat, defaultLng], 13);
    
    // Agregar capa de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Marcador del vehículo (icono de camión)
    vehicleMarker = L.marker([defaultLat, defaultLng], {
        icon: L.icon({
            iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDQwIDQwIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxOCIgZmlsbD0iIzIxOTZmMyIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiLz48dGV4dCB4PSIyMCIgeT0iMjgiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyNCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+🚚</dGV4dD48L3N2Zz4=',
            iconSize: [40, 40],
            iconAnchor: [20, 40]
        })
    }).addTo(map);
    
    // Popup del vehículo
    vehicleMarker.bindPopup(`
        <div style="text-align: center; padding: 10px;">
            <h6>🚛 {{ entrega.vehiculo_placa }}</h6>
            <p><strong>Conductor:</strong> {{ entrega.conductor_nombre }}</p>
            <p><strong>Teléfono:</strong> {{ entrega.conductor_telefono }}</p>
            <small>Última actualización: <span id="popup-tiempo">${new Date().toLocaleTimeString()}</span></small>
        </div>
    `);
    
    // Marcador de destino si hay coordenadas
    {% if entrega.pedido.latitud_entrega and entrega.pedido.longitud_entrega %}
    destinationMarker = L.marker([{{ entrega.pedido.latitud_entrega }}, {{ entrega.pedido.longitud_entrega }}], {
        icon: L.icon({
            iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDQwIDQwIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxOCIgZmlsbD0iIzRjYWY1MCIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiLz48dGV4dCB4PSIyMCIgeT0iMjgiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyNCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+🏠</dGV4dD48L3N2Zz4=',
            iconSize: [40, 40],
            iconAnchor: [20, 40]
        })
    }).addTo(map);
    
    destinationMarker.bindPopup(`
        <div style="text-align: center; padding: 10px;">
            <h6>🏠 Dirección de Entrega</h6>
            <p>{{ entrega.pedido.direccion_entrega }}</p>
        </div>
    `);
    
    // Ajustar vista para mostrar ambos marcadores
    const group = new L.featureGroup([vehicleMarker, destinationMarker]);
    map.fitBounds(group.getBounds().pad(0.1));
    {% endif %}
    
    // Cargar ubicación inicial
    actualizarUbicacionVehiculo();
}

// Actualizar ubicación del vehículo
function actualizarUbicacionVehiculo() {
    fetch(`{% url 'pedidos:api_ubicacion_entrega' pedido.id_pedido %}`)
        .then(response => response.json())
        .then(data => {
            if (data.latitud && data.longitud && vehicleMarker) {
                // Actualizar posición del marcador
                vehicleMarker.setLatLng([data.latitud, data.longitud]);
                
                // Centrar mapa en la nueva posición
                map.setView([data.latitud, data.longitud], map.getZoom());
                
                // Actualizar información en pantalla
                if (data.ultima_actualizacion) {
                    const fecha = new Date(data.ultima_actualizacion);
                    document.getElementById('ultima-actualizacion').textContent = fecha.toLocaleTimeString();
                    
                    // Actualizar tiempo en popup
                    const popupTiempo = document.getElementById('popup-tiempo');
                    if (popupTiempo) {
                        popupTiempo.textContent = fecha.toLocaleTimeString();
                    }
                }
                
                if (data.distancia_restante_km && document.getElementById('distancia-restante')) {
                    document.getElementById('distancia-restante').textContent = data.distancia_restante_km + ' km';
                }
                
                // Actualizar ETA
                if (data.tiempo_estimado_llegada && document.getElementById('eta-countdown')) {
                    const eta = new Date(data.tiempo_estimado_llegada);
                    document.getElementById('eta-countdown').textContent = eta.toLocaleTimeString();
                }
                
                console.log('✅ Ubicación actualizada:', data.latitud, data.longitud);
            } else {
                console.log('⚠️ No hay datos de ubicación disponibles');
            }
        })
        .catch(error => {
            console.error('❌ Error al actualizar ubicación:', error);
        });
}

// Iniciar actualizaciones automáticas cada 15 segundos
setInterval(actualizarUbicacionVehiculo, 15000);
{% endif %}

// Actualizar todos los datos
function actualizarDatos() {
    location.reload();
}

// Llamar al conductor
function llamarConductor() {
    window.open('tel:{{ entrega.conductor_telefono }}');
}

// Auto-actualizar página cada 2 minutos
setInterval(function() {
    if (estadoEntrega === 'en_camino') {
        actualizarDatos();
    }
}, 120000);

// Notificaciones del navegador
function mostrarNotificacion(titulo, mensaje) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(titulo, {
            body: mensaje,
            icon: '/static/logo_multiandamios.png'
        });
    }
}

// Solicitar permisos de notificación
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Contador regresivo para ETA
{% if entrega.tiempo_estimado_llegada and entrega.estado_entrega == 'en_camino' %}
function actualizarContadorETA() {
    const eta = new Date('{{ entrega.tiempo_estimado_llegada|date:"c" }}');
    const ahora = new Date();
    const diferencia = eta.getTime() - ahora.getTime();
    
    if (diferencia > 0) {
        const minutos = Math.floor(diferencia / (1000 * 60));
        const horas = Math.floor(minutos / 60);
        const minutosRestantes = minutos % 60;
        
        if (horas > 0) {
            document.getElementById('eta-countdown').textContent = `${horas}h ${minutosRestantes}m`;
        } else {
            document.getElementById('eta-countdown').textContent = `${minutosRestantes}m`;
        }
    } else {
        document.getElementById('eta-countdown').textContent = 'Llegando...';
    }
}

// Actualizar contador cada minuto
setInterval(actualizarContadorETA, 60000);
actualizarContadorETA();
{% endif %}

// Efectos visuales
document.addEventListener('DOMContentLoaded', function() {
    // Animación de entrada para las tarjetas
    const cards = document.querySelectorAll('.status-card, .vehicle-card, .contact-card, .eta-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
</script>

<!-- Leaflet (OpenStreetMap) API -->
{% if entrega.estado_entrega == 'en_camino' and puede_ver_ubicacion %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initMap();
});
</script>
{% endif %}

{% endblock %}
TEMPLATE_EOF

echo "✅ Template corregido creado: template_seguimiento_cliente_corregido.html"
echo ""
echo "📤 Para subir a PythonAnywhere, ejecutar:"
echo ""
echo "1. Conectar SSH:"
echo "   ssh dalej@ssh.pythonanywhere.com"
echo ""
echo "2. Navegar al proyecto:"
echo "   cd /home/dalej/multiandamios"
echo ""
echo "3. Hacer backup:"
echo "   cp pedidos/templates/entregas/seguimiento_cliente.html pedidos/templates/entregas/seguimiento_cliente_backup.html"
echo ""
echo "4. Subir nuevo template (copiar y pegar el contenido del archivo creado)"
echo "   nano pedidos/templates/entregas/seguimiento_cliente.html"
echo ""
echo "5. Reiniciar aplicación:"
echo "   touch /var/www/dalej_pythonanywhere_com_wsgi.py"
echo ""
echo "🧪 Probar en: https://dalej.pythonanywhere.com/panel/entregas/cliente/seguimiento/74/"
