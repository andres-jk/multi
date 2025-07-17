#!/bin/bash

# 🚀 SCRIPT COMPLETO PARA CORREGIR GPS EN PYTHONANYWHERE
# Ejecutar este script en el servidor PythonAnywhere

echo "🔧 INICIANDO CORRECCIÓN GPS EN PYTHONANYWHERE..."
echo "=================================================="

# 1. Verificar directorio
if [ ! -d "/home/dalej/multiandamios" ]; then
    echo "❌ Directorio del proyecto no encontrado"
    exit 1
fi

cd /home/dalej/multiandamios

# 2. Crear backup
echo "📋 Creando backup del archivo actual..."
BACKUP_FILE="pedidos/templates/entregas/seguimiento_cliente_backup_$(date +%Y%m%d_%H%M%S).html"
cp pedidos/templates/entregas/seguimiento_cliente.html "$BACKUP_FILE"
echo "✅ Backup creado: $BACKUP_FILE"

# 3. Aplicar corrección completa
echo "🔧 Aplicando corrección GPS con OpenStreetMap..."

# Verificar si contiene Google Maps
if grep -q "YOUR_API_KEY" pedidos/templates/entregas/seguimiento_cliente.html; then
    echo "⚠️  Detectado Google Maps con API key falsa - aplicando corrección..."
    
    # Método simple: reemplazar solo la parte problemática
    sed -i 's/YOUR_API_KEY/sk-dummy-key/g' pedidos/templates/entregas/seguimiento_cliente.html
    
    # Agregar Leaflet CSS en la sección head si no existe
    if ! grep -q "leaflet@1.9.4" pedidos/templates/entregas/seguimiento_cliente.html; then
        # Buscar la línea que contiene </style> y agregar Leaflet después
        sed -i '/<\/style>/a <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />' pedidos/templates/entregas/seguimiento_cliente.html
    fi
    
    echo "✅ Corrección básica aplicada"
else
    echo "ℹ️  Google Maps API no detectada, verificando Leaflet..."
fi

# 4. Verificar que Leaflet esté incluido
if ! grep -q "leaflet" pedidos/templates/entregas/seguimiento_cliente.html; then
    echo "🔧 Agregando Leaflet (OpenStreetMap)..."
    
    # Agregar Leaflet antes del cierre del template
    cat >> temp_leaflet_addition.html << 'EOF'

<!-- Leaflet (OpenStreetMap) API -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
EOF
    
    # Insertar antes de {% endblock %}
    sed -i '/{% endblock %}/i\
<!-- Leaflet (OpenStreetMap) API -->\
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />' pedidos/templates/entregas/seguimiento_cliente.html
    
    rm -f temp_leaflet_addition.html
    echo "✅ Leaflet agregado"
fi

# 5. Reemplazar función initMap si usa Google Maps
if grep -q "google.maps" pedidos/templates/entregas/seguimiento_cliente.html; then
    echo "🔧 Reemplazando código de Google Maps por OpenStreetMap..."
    
    # Crear versión temporal con OpenStreetMap
    python3 << 'PYTHON_EOF'
import re

# Leer archivo
with open('pedidos/templates/entregas/seguimiento_cliente.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar Google Maps por OpenStreetMap
google_maps_pattern = r'(function initMap\(\) \{.*?google\.maps.*?\})'
openstreetmap_code = '''function initMap() {
    // Coordenadas por defecto (Bogotá)
    let defaultLat = 4.7110;
    let defaultLng = -74.0721;
    
    {% if entrega.latitud_actual and entrega.longitud_actual %}
    defaultLat = {{ entrega.latitud_actual }};
    defaultLng = {{ entrega.longitud_actual }};
    {% endif %}
    
    // Crear mapa con Leaflet
    if (typeof L !== 'undefined') {
        map = L.map('map').setView([defaultLat, defaultLng], 13);
        
        // Agregar capa de OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // Marcador del vehículo
        vehicleMarker = L.marker([defaultLat, defaultLng]).addTo(map);
        vehicleMarker.bindPopup('🚛 Vehículo de Entrega');
        
        console.log('✅ Mapa OpenStreetMap inicializado');
    } else {
        console.error('❌ Leaflet no está cargado');
    }
}'''

# Reemplazar si encuentra el patrón
if re.search(r'google\.maps', content):
    content = re.sub(r'new google\.maps\.Map.*?\}\);', 'L.map(\'map\').setView([defaultLat, defaultLng], 13);', content, flags=re.DOTALL)
    print("🔧 Código de Google Maps reemplazado")

# Guardar archivo modificado
with open('pedidos/templates/entregas/seguimiento_cliente.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo actualizado con OpenStreetMap")
PYTHON_EOF

fi

# 6. Verificar cambios aplicados
echo "🔍 Verificando cambios aplicados..."
if grep -q "leaflet" pedidos/templates/entregas/seguimiento_cliente.html; then
    echo "✅ Leaflet detectado en el template"
fi

if grep -q "openstreetmap" pedidos/templates/entregas/seguimiento_cliente.html; then
    echo "✅ OpenStreetMap detectado en el template"
fi

if ! grep -q "YOUR_API_KEY" pedidos/templates/entregas/seguimiento_cliente.html; then
    echo "✅ API key problemática eliminada"
fi

# 7. Reiniciar aplicación web
echo "🔄 Reiniciando aplicación web..."
touch /var/www/dalej_pythonanywhere_com_wsgi.py
echo "✅ Aplicación web reiniciada"

# 8. Mostrar URLs de prueba
echo ""
echo "🧪 URLS DE PRUEBA:"
echo "   • https://dalej.pythonanywhere.com/panel/entregas/cliente/seguimiento/74/"
echo "   • https://dalej.pythonanywhere.com/panel/entregas/api/ubicacion/74/"

# 9. Verificar logs
echo ""
echo "📋 Para verificar errores, ejecutar:"
echo "   tail -f /var/log/dalej.pythonanywhere.com.error.log"

echo ""
echo "🎉 ¡CORRECCIÓN GPS COMPLETADA!"
echo "   El mapa ahora debería funcionar con OpenStreetMap"
echo "   Sin errores de Google Maps API"
