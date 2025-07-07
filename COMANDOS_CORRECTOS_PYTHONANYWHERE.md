# 🔧 COMANDOS CORRECTOS PARA PYTHONANYWHERE

## ❌ COMANDO INCORRECTO:
```bash
p SETTINGS_ULTRA_SIMPLE_PYTHONANYWHERE.py multiandamios/settings.py
```

## ✅ COMANDOS CORRECTOS:

### 1. Copiar el archivo:
```bash
cp SETTINGS_ULTRA_SIMPLE_PYTHONANYWHERE.py multiandamios/settings.py
```

### 2. Verificar que se copió correctamente:
```bash
ls -la multiandamios/settings.py
```

### 3. Ver las primeras líneas para confirmar:
```bash
head -20 multiandamios/settings.py
```

### 4. Probar que funciona:
```bash
python manage.py check
```

### 5. Si funciona, continuar con:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. También actualizar el WSGI:
```bash
cp WSGI_PYTHONANYWHERE_COMPLETO.py multiandamios/wsgi.py
```

### 7. Verificar el WSGI:
```bash
head -10 multiandamios/wsgi.py
```

## 📋 RESUMEN DE COMANDOS EN ORDEN:

```bash
cd /home/Dalej/multi
git pull origin main
cp SETTINGS_ULTRA_SIMPLE_PYTHONANYWHERE.py multiandamios/settings.py
cp WSGI_PYTHONANYWHERE_COMPLETO.py multiandamios/wsgi.py
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

## 🎯 DESPUÉS DE ESTOS COMANDOS:
1. Ve a la pestaña "Web" en PythonAnywhere
2. Haz clic en "Reload dalej.pythonanywhere.com"
3. Visita https://dalej.pythonanywhere.com

¡Usa `cp` (copy) en lugar de `p`! 🚀
