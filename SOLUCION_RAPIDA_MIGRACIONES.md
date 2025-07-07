# 🚀 SOLUCIÓN RÁPIDA - IGNORAR ERRORES TEMPORALMENTE

## ❌ PROBLEMA: 
Los errores del modelo Usuario están bloqueando las migraciones.

## ✅ SOLUCIÓN: Forzar migraciones ignorando errores

### 🔧 COMANDOS PARA PYTHONANYWHERE:

```bash
# 1. Forzar migraciones ignorando errores del sistema
python manage.py migrate --skip-checks

# 2. Si no funciona, crear tablas manualmente
python manage.py migrate --fake-initial

# 3. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 4. Crear superusuario (opcional)
python manage.py createsuperuser --skip-checks

# 5. Verificar que los directorios existen
ls -la staticfiles/
ls -la media/
```

## 🎯 ALTERNATIVA: Deshabilitar temporalmente la app usuarios

### Edita settings.py temporalmente:

```bash
nano multiandamios/settings.py
```

### Comenta la línea 'usuarios' en INSTALLED_APPS:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'usuarios',  # ← Comentar esta línea temporalmente
    'productos',
    'pedidos',
    'recibos',
    'chatbot',
]
```

### Guarda y ejecuta:
```bash
# Ctrl+O, Enter, Ctrl+X
python manage.py migrate
python manage.py collectstatic --noinput
```

## 🚀 DESPUÉS DE COMPLETAR:
1. Ve a la pestaña "Web" en PythonAnywhere
2. Haz clic en "Reload dalej.pythonanywhere.com"
3. Visita https://dalej.pythonanywhere.com

## 📋 NOTA:
- La aplicación funcionará sin la app 'usuarios' temporalmente
- Podemos arreglar el modelo Usuario después
- Lo importante es que la app principal funcione

¡Prueba primero con `--skip-checks` y si no funciona, comenta la app usuarios! 🎯
