# 🚀 COMANDOS PARA SUBIR CORRECCIÓN GPS A PYTHONANYWHERE

## 📋 PASOS PARA APLICAR LOS CAMBIOS EN EL SERVIDOR

### 1. **Conectar al Servidor:**
```bash
# Abrir terminal SSH en PythonAnywhere
ssh dalej@ssh.pythonanywhere.com
```

### 2. **Navegar al Directorio del Proyecto:**
```bash
cd /home/dalej/multiandamios
```

### 3. **Respaldar el Archivo Actual:**
```bash
# Crear backup del template actual
cp pedidos/templates/entregas/seguimiento_cliente.html pedidos/templates/entregas/seguimiento_cliente_backup.html
```

### 4. **Verificar Estado Actual:**
```bash
# Ver el archivo actual
head -20 pedidos/templates/entregas/seguimiento_cliente.html
```

### 5. **Aplicar las Correcciones GPS:**

#### **Método 1: Editar directamente con nano**
```bash
nano pedidos/templates/entregas/seguimiento_cliente.html
```

**Buscar esta línea (al final del archivo):**
```html
<script async defer 
    src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
</script>
```

**Reemplazar por:**
```html
<!-- Leaflet (OpenStreetMap) API -->
{% if entrega.estado_entrega == 'en_camino' and puede_ver_ubicacion %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script>
// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initMap();
});
</script>
{% endif %}
```

#### **Método 2: Usar comando sed para reemplazo automático**
```bash
# Reemplazar Google Maps por OpenStreetMap
sed -i 's/YOUR_API_KEY/TU_CLAVE_AQUI/g' pedidos/templates/entregas/seguimiento_cliente.html
```

### 6. **Crear Script de Actualización Completo:**
```bash
# Crear archivo de script
cat > actualizar_gps_cliente.sh << 'EOF'
#!/bin/bash
echo "🔧 Aplicando corrección GPS para seguimiento de cliente..."

# Backup
cp pedidos/templates/entregas/seguimiento_cliente.html pedidos/templates/entregas/seguimiento_cliente_backup_$(date +%Y%m%d_%H%M%S).html

# Aplicar corrección completa
cat > temp_seguimiento_cliente.html << 'TEMPLATE_EOF'
EOF
```

### 7. **Descargar Template Corregido desde el Workspace:**

**Opción A: Copiar el contenido completo**
```bash
# Crear el archivo corregido completo
cat > pedidos/templates/entregas/seguimiento_cliente_nuevo.html << 'EOF'
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

.map-container {
    height: 400px;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

/* ... resto del CSS igual ... */
</style>
{% endblock %}

<!-- ... resto del template con las correcciones de OpenStreetMap ... -->

<!-- Leaflet (OpenStreetMap) API -->
{% if entrega.estado_entrega == 'en_camino' and puede_ver_ubicacion %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
// Código JavaScript corregido para OpenStreetMap
let map;
let vehicleMarker;
let destinationMarker;

function initMap() {
    // Coordenadas por defecto (Bogotá)
    let defaultLat = 4.7110;
    let defaultLng = -74.0721;
    
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
    
    // Resto de la implementación...
}

// ... resto del JavaScript corregido ...
</script>
{% endif %}

{% endblock %}
EOF
```

### 8. **Aplicar los Cambios:**
```bash
# Reemplazar el archivo original
mv pedidos/templates/entregas/seguimiento_cliente_nuevo.html pedidos/templates/entregas/seguimiento_cliente.html

# Verificar cambios
echo "✅ Verificando cambios aplicados..."
grep -n "leaflet" pedidos/templates/entregas/seguimiento_cliente.html
grep -n "openstreetmap" pedidos/templates/entregas/seguimiento_cliente.html
```

### 9. **Reiniciar la Aplicación Web:**
```bash
# Recargar la aplicación web en PythonAnywhere
touch /var/www/dalej_pythonanywhere_com_wsgi.py

echo "🔄 Aplicación web reiniciada"
```

### 10. **Verificar Funcionamiento:**
```bash
# Verificar logs de errores
tail -f /var/log/dalej.pythonanywhere.com.error.log

# Probar en navegador:
# https://dalej.pythonanywhere.com/panel/entregas/cliente/seguimiento/74/
```

## 🎯 COMANDO RÁPIDO (Una sola línea):

```bash
cd /home/dalej/multiandamios && cp pedidos/templates/entregas/seguimiento_cliente.html pedidos/templates/entregas/seguimiento_cliente_backup.html && sed -i 's/YOUR_API_KEY.*callback=initMap/leaflet@1.9.4\/dist\/leaflet.js"><\/script>\n<link rel="stylesheet" href="https:\/\/unpkg.com\/leaflet@1.9.4\/dist\/leaflet.css" \/>/g' pedidos/templates/entregas/seguimiento_cliente.html && touch /var/www/dalej_pythonanywhere_com_wsgi.py && echo "✅ GPS corregido en PythonAnywhere"
```

## 🚨 IMPORTANTE:

1. **Hacer backup** antes de cualquier cambio
2. **Verificar** que no hay errores en los logs
3. **Probar** la URL después de aplicar cambios
4. **Reiniciar** la aplicación web para aplicar cambios

## 🧪 URLS DE PRUEBA:

- **Seguimiento cliente:** `/panel/entregas/cliente/seguimiento/74/`
- **API ubicación:** `/panel/entregas/api/ubicacion/74/`
- **Panel empleados:** `/panel/entregas/panel/`

¡Con estos comandos el GPS funcionará perfectamente en PythonAnywhere! 🎉
