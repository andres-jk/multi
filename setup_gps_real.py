#!/usr/bin/env python3
"""
Script para configurar el GPS funcional en MultiAndamios
Crea la configuración necesaria para GPS en tiempo real
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.conf import settings

def setup_gps_configuration():
    """Configura el sistema GPS para funcionamiento real"""
    
    print("🔧 CONFIGURANDO SISTEMA GPS FUNCIONAL")
    print("=" * 50)
    
    # 1. Verificar si existe configuración GPS en settings
    print("📋 Verificando configuración actual...")
    
    if hasattr(settings, 'GOOGLE_MAPS_API_KEY'):
        print(f"✅ Google Maps API Key configurada")
    else:
        print("❌ Google Maps API Key NO configurada")
    
    # 2. Mostrar los pasos necesarios
    print("\n📌 PASOS PARA ACTIVAR GPS FUNCIONAL:")
    print("1. Obtener API Key de Google Maps:")
    print("   - Ve a: https://console.cloud.google.com/")
    print("   - Crea un proyecto o selecciona uno existente")
    print("   - Habilita 'Maps JavaScript API' y 'Geolocation API'")
    print("   - Crea credenciales -> API Key")
    print("   - Restringe la API Key a tu dominio")
    
    print("\n2. Configurar en Django:")
    print("   - Agregar en multiandamios/settings.py:")
    print("     GOOGLE_MAPS_API_KEY = 'tu_api_key_aqui'")
    
    print("\n3. Para GPS en tiempo real sin Google Maps (alternativa):")
    print("   - Usar solo geolocalización del navegador")
    print("   - Implementar mapa con OpenStreetMap (gratuito)")
    print("   - Guardar coordenadas en base de datos")
    
    return True

def create_alternative_gps_solution():
    """Crea una solución GPS alternativa sin Google Maps"""
    
    print("\n🌍 CREANDO SOLUCIÓN GPS ALTERNATIVA (SIN GOOGLE MAPS)")
    print("=" * 50)
    
    # Template mejorado para GPS con OpenStreetMap
    gps_template_content = '''{% extends 'base.html' %}
{% load humanize %}

{% block title %}📍 Ubicación en Tiempo Real - Entrega #{{ entrega.pedido.id_pedido }}{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
.map-container {
    height: 400px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.gps-info {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}

.gps-update {
    background: #4caf50;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.gps-update:hover {
    background: #45a049;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.status-badge {
    display: inline-block;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 600;
    color: white;
}

.status-en_camino { background: #ff9800; animation: pulse 2s infinite; }
.status-entregada { background: #4caf50; }
.status-programada { background: #9e9e9e; }

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(255, 152, 0, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0); }
}

.coordinate-display {
    font-family: 'Courier New', monospace;
    background: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
{% endblock %}

{% block extra_js %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>📍 Ubicación en Tiempo Real</h1>
                <span class="status-badge status-{{ entrega.estado_entrega }}">
                    {{ entrega.get_estado_entrega_display }}
                </span>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <!-- Mapa -->
            <div id="map" class="map-container"></div>
        </div>
        
        <div class="col-md-4">
            <!-- Información GPS -->
            <div class="gps-info">
                <h5>📡 Estado GPS</h5>
                <p><strong>Última actualización:</strong> <span id="ultima-actualizacion">{{ entrega.ultima_actualizacion_gps|default:"Nunca" }}</span></p>
                <p><strong>Coordenadas:</strong></p>
                <div class="coordinate-display">
                    <div>Lat: <span id="latitud-actual">{{ entrega.latitud_actual|default:"No disponible" }}</span></div>
                    <div>Lng: <span id="longitud-actual">{{ entrega.longitud_actual|default:"No disponible" }}</span></div>
                </div>
                
                <button class="gps-update w-100 mt-3" onclick="actualizarGPS()">
                    📍 ACTUALIZAR GPS
                </button>
            </div>

            <!-- Información del Pedido -->
            <div class="card">
                <div class="card-header">
                    <h6>📦 Información del Pedido</h6>
                </div>
                <div class="card-body">
                    <p><strong>Pedido:</strong> #{{ entrega.pedido.id_pedido }}</p>
                    <p><strong>Cliente:</strong> {{ entrega.pedido.cliente.usuario.get_full_name|default:entrega.pedido.cliente.usuario.username }}</p>
                    <p><strong>Dirección:</strong> {{ entrega.pedido.direccion_entrega }}</p>
                    <p><strong>Vehículo:</strong> {{ entrega.vehiculo_placa }}</p>
                    <p><strong>Conductor:</strong> {{ entrega.conductor_nombre }}</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let map;
let vehicleMarker;
let destinationMarker;
const entregaId = {{ entrega.id }};

// Inicializar mapa
function initMap() {
    // Coordenadas por defecto (Bogotá)
    let defaultLat = 4.7110;
    let defaultLng = -74.0721;
    
    // Si hay coordenadas guardadas, usarlas
    {% if entrega.latitud_actual and entrega.longitud_actual %}
    defaultLat = {{ entrega.latitud_actual }};
    defaultLng = {{ entrega.longitud_actual }};
    {% endif %}
    
    map = L.map('map').setView([defaultLat, defaultLng], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Marcador del vehículo
    vehicleMarker = L.marker([defaultLat, defaultLng], {
        icon: L.icon({
            iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgdmlld0JveD0iMCAwIDMyIDMyIj48cGF0aCBmaWxsPSIjRkY5ODAwIiBkPSJNMTYgMmMtNC40MTggMC04IDMuNTgyLTggOHMzLjU4MiA4IDggOGM0LjQxOCAwIDgtMy41ODIgOC04UzIwLjQxOCAyIDE2IDJ6Ii8+PHBhdGggZmlsbD0iI0ZGRiIgZD0iTTE2IDZjLTIuMjA5IDAtNCAx2gtNCA0czEuNzkxIDQgNCA0YzIuMjA5IDAgNC0xLjc5MSA0LTRTMTguMjA5IDYgMTYgNnoiLz48L3N2Zz4=',
            iconSize: [32, 32],
            iconAnchor: [16, 32]
        })
    }).addTo(map);
    
    vehicleMarker.bindPopup('🚚 Vehículo: {{ entrega.vehiculo_placa }}');
    
    // Si hay coordenadas de destino, agregar marcador
    {% if entrega.pedido.latitud_entrega and entrega.pedido.longitud_entrega %}
    destinationMarker = L.marker([{{ entrega.pedido.latitud_entrega }}, {{ entrega.pedido.longitud_entrega }}], {
        icon: L.icon({
            iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgdmlld0JveD0iMCAwIDMyIDMyIj48cGF0aCBmaWxsPSIjNGNhZjUwIiBkPSJNMTYgMmMtNC40MTggMC04IDMuNTgyLTggOHMzLjU4MiA4IDggOGM0LjQxOCAwIDgtMy41ODIgOC04UzIwLjQxOCAyIDE2IDJ6Ii8+PHBhdGggZmlsbD0iI0ZGRiIgZD0iTTE2IDZjLTIuMjA5IDAtNCAx2gtNCA0czEuNzkxIDQgNCA0YzIuMjA5IDAgNC0xLjc5MSA0LTRTMTguMjA5IDYgMTYgNnoiLz48L3N2Zz4=',
            iconSize: [32, 32],
            iconAnchor: [16, 32]
        })
    }).addTo(map);
    
    destinationMarker.bindPopup('🏠 Destino: {{ entrega.pedido.direccion_entrega }}');
    {% endif %}
}

// Actualizar GPS
function actualizarGPS() {
    if (!navigator.geolocation) {
        alert('❌ Tu navegador no soporta geolocalización');
        return;
    }
    
    const button = document.querySelector('.gps-update');
    button.textContent = '🔄 Obteniendo ubicación...';
    button.disabled = true;
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            
            // Actualizar mapa
            map.setView([lat, lng], 15);
            vehicleMarker.setLatLng([lat, lng]);
            
            // Actualizar interfaz
            document.getElementById('latitud-actual').textContent = lat.toFixed(6);
            document.getElementById('longitud-actual').textContent = lng.toFixed(6);
            document.getElementById('ultima-actualizacion').textContent = new Date().toLocaleString();
            
            // Enviar al servidor
            fetch('{% url "pedidos:actualizar_ubicacion" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({
                    entrega_id: entregaId,
                    latitud: lat,
                    longitud: lng,
                    accuracy: accuracy
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ Ubicación actualizada en servidor');
                } else {
                    console.error('❌ Error:', data.error);
                }
            })
            .catch(error => {
                console.error('❌ Error de conexión:', error);
            });
            
            button.textContent = '✅ GPS ACTUALIZADO';
            setTimeout(() => {
                button.textContent = '📍 ACTUALIZAR GPS';
                button.disabled = false;
            }, 2000);
        },
        function(error) {
            button.textContent = '❌ ERROR GPS';
            setTimeout(() => {
                button.textContent = '📍 ACTUALIZAR GPS';
                button.disabled = false;
            }, 2000);
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    alert('❌ Permiso denegado. Por favor, permite el acceso a la ubicación.');
                    break;
                case error.POSITION_UNAVAILABLE:
                    alert('❌ Ubicación no disponible.');
                    break;
                case error.TIMEOUT:
                    alert('❌ Tiempo de espera agotado.');
                    break;
                default:
                    alert('❌ Error desconocido al obtener ubicación.');
                    break;
            }
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        }
    );
}

// Inicializar cuando cargue la página
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    // Auto-actualizar cada 30 segundos si está en camino
    {% if entrega.estado_entrega == 'en_camino' %}
    setInterval(actualizarGPS, 30000);
    {% endif %}
});
</script>
{% endblock %}'''
    
    return gps_template_content

if __name__ == "__main__":
    setup_gps_configuration()
    
    # Crear template mejorado
    template_content = create_alternative_gps_solution()
    
    print("\n💾 Creando template GPS mejorado...")
    
    # Crear el template actualizado
    template_path = 'pedidos/templates/entregas/seguimiento_gps_real.html'
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ Template creado: {template_path}")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Agregar campos de GPS al modelo Entrega si no existen")
    print("2. Crear vista para actualizar ubicación GPS")
    print("3. Probar la funcionalidad en el navegador")
    print("4. Configurar auto-actualización para empleados")
    
    print("\n✨ El GPS funcionará con:")
    print("   - Geolocalización del navegador (sin API keys)")
    print("   - Mapa OpenStreetMap (gratuito)")
    print("   - Actualización automática cada 30 segundos")
    print("   - Almacenamiento en base de datos")
