# GUÍA COMPLETA DE DESPLIEGUE EN PYTHONANYWHERE

## PASOS PARA CONFIGURAR EL PROYECTO EN PYTHONANYWHERE

### 1. En PythonAnywhere - Consola Bash

```bash
# Navegar al directorio del proyecto
cd /home/Dalej/multi

# Verificar que los archivos están ahí
ls -la

# Crear directorios necesarios
mkdir -p staticfiles
mkdir -p media

# Verificar permisos
ls -la staticfiles
ls -la media
```

### 2. Reemplazar archivos de configuración

**A. Reemplazar settings.py:**
- Abre el archivo: `nano multiandamios/settings.py`
- Elimina todo el contenido (Ctrl+K varias veces)
- Copia el contenido completo de `SETTINGS_PYTHONANYWHERE_COMPLETO.py`
- Guarda: Ctrl+O, Enter, Ctrl+X

**B. Reemplazar wsgi.py:**
- Abre el archivo: `nano multiandamios/wsgi.py`
- Elimina todo el contenido (Ctrl+K varias veces)
- Copia el contenido completo de `WSGI_PYTHONANYWHERE_COMPLETO.py`
- Guarda: Ctrl+O, Enter, Ctrl+X

### 3. Ejecutar comandos Django

```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario (si no existe)
python manage.py createsuperuser

# Verificar que todo esté correcto
python manage.py check
```

### 4. Configurar la aplicación web

1. Ve a la pestaña "Web" en PythonAnywhere
2. Haz clic en "Reload dalej.pythonanywhere.com"
3. Verifica que:
   - Source code: `/home/Dalej/multi`
   - WSGI configuration file: `/home/Dalej/multi/multiandamios/wsgi.py`
   - Static files: URL `/static/` → Directory `/home/Dalej/multi/staticfiles`
   - Static files: URL `/media/` → Directory `/home/Dalej/multi/media`

### 5. Probar la aplicación

- Visita: https://dalej.pythonanywhere.com
- Deberías ver tu aplicación funcionando correctamente

## SOLUCIÓN A PROBLEMAS COMUNES

### Si hay errores de permisos:
```bash
chmod 755 /home/Dalej/multi
chmod 755 /home/Dalej/multi/staticfiles
chmod 755 /home/Dalej/multi/media
```

### Si la base de datos no se crea:
```bash
python manage.py flush --noinput
python manage.py migrate
```

### Si los archivos estáticos no se cargan:
```bash
python manage.py collectstatic --clear --noinput
```

## VERIFICACIÓN FINAL

Después de completar todos los pasos, verifica que:
1. ✅ La aplicación carga sin errores
2. ✅ Los estilos CSS se aplican correctamente
3. ✅ Las imágenes se muestran
4. ✅ El login funciona
5. ✅ El admin funciona en `/admin`

¡Tu aplicación debería estar funcionando perfectamente en PythonAnywhere!
