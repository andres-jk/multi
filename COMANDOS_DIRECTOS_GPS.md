# 🚀 COMANDOS DIRECTOS PARA PYTHONANYWHERE

## ⚡ CORRECCIÓN RÁPIDA (Copiar y pegar en terminal SSH):

```bash
# 1. Conectar y navegar
ssh dalej@ssh.pythonanywhere.com
cd /home/dalej/multiandamios

# 2. Backup y corrección rápida
cp pedidos/templates/entregas/seguimiento_cliente.html pedidos/templates/entregas/seguimiento_cliente_backup.html && sed -i 's/YOUR_API_KEY/leaflet-openstreetmap/g' pedidos/templates/entregas/seguimiento_cliente.html && touch /var/www/dalej_pythonanywhere_com_wsgi.py

# 3. Verificar cambio
grep -n "leaflet-openstreetmap" pedidos/templates/entregas/seguimiento_cliente.html
```

## 🔧 CORRECCIÓN COMPLETA (Paso a paso):

### Paso 1: Conectar al servidor
```bash
ssh dalej@ssh.pythonanywhere.com
```

### Paso 2: Ir al directorio del proyecto
```bash
cd /home/dalej/multiandamios
```

### Paso 3: Hacer backup
```bash
cp pedidos/templates/entregas/seguimiento_cliente.html pedidos/templates/entregas/seguimiento_cliente_backup_$(date +%Y%m%d).html
```

### Paso 4: Editar el archivo problemático
```bash
nano pedidos/templates/entregas/seguimiento_cliente.html
```

**Buscar al final del archivo (Ctrl+W para buscar):**
```
YOUR_API_KEY
```

**Reemplazar por:**
```
dummy-key-fixed
```

**Luego buscar:**
```html
<script async defer 
    src="https://maps.googleapis.com/maps/api/js?key=dummy-key-fixed&callback=initMap">
</script>
```

**Y reemplazar por:**
```html
<!-- OpenStreetMap con Leaflet -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof initMap === 'function') {
        initMap();
    }
});
</script>
```

### Paso 5: Guardar y salir
```
Ctrl+O (guardar)
Enter (confirmar)
Ctrl+X (salir)
```

### Paso 6: Reiniciar aplicación
```bash
touch /var/www/dalej_pythonanywhere_com_wsgi.py
```

### Paso 7: Verificar
```bash
echo "✅ Verificando cambios..."
grep -n "leaflet" pedidos/templates/entregas/seguimiento_cliente.html
echo "🧪 Probar en: https://dalej.pythonanywhere.com/panel/entregas/cliente/seguimiento/74/"
```

## 🎯 VERIFICACIÓN FINAL:

### Comprobar que funciona:
1. Abrir: https://dalej.pythonanywhere.com/panel/entregas/cliente/seguimiento/74/
2. Verificar que NO aparece el error de Google Maps
3. Verificar que SÍ aparece un mapa de OpenStreetMap

### Si aún hay problemas:
```bash
# Ver logs de errores
tail -20 /var/log/dalej.pythonanywhere.com.error.log

# Verificar archivos estáticos
ls -la static/

# Reiniciar nuevamente
touch /var/www/dalej_pythonanywhere_com_wsgi.py
```

## 📋 COMANDOS DE UNA LÍNEA:

### Corrección básica:
```bash
cd /home/dalej/multiandamios && sed -i 's/YOUR_API_KEY/fixed-key/g' pedidos/templates/entregas/seguimiento_cliente.html && touch /var/www/dalej_pythonanywhere_com_wsgi.py
```

### Agregar Leaflet:
```bash
sed -i '/{% endblock %}/i\<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />' pedidos/templates/entregas/seguimiento_cliente.html
```

### Verificar resultado:
```bash
curl -s "https://dalej.pythonanywhere.com/panel/entregas/cliente/seguimiento/74/" | grep -i "error\|leaflet\|google"
```

¡Con estos comandos el GPS funcionará en PythonAnywhere! 🎉
