# 🚨 DALEJ: EL ERROR PERSISTE - SOLUCIÓN PASO A PASO

## ❌ PROBLEMA:
El error `DisallowedHost` sigue apareciendo, lo que significa que `ALLOWED_HOSTS` no se ha corregido correctamente.

## ✅ SOLUCIÓN PASO A PASO:

### PASO 1: VERIFICAR EL ARCHIVO ACTUAL
```bash
# Ejecuta esto para ver el contenido actual
cat multiandamios/settings.py | grep -A 2 -B 2 ALLOWED_HOSTS
```

### PASO 2: EDITAR MANUALMENTE
```bash
# Abrir el archivo
nano multiandamios/settings.py
```

### PASO 3: BUSCAR LA LÍNEA EXACTA
Busca una de estas líneas:
```python
ALLOWED_HOSTS = []
```
o
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### PASO 4: REEMPLAZAR CON EXACTAMENTE ESTO:
```python
ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']
```

### PASO 5: GUARDAR Y VERIFICAR
```bash
# Guardar: Ctrl + X, Y, Enter
# Verificar el cambio:
cat multiandamios/settings.py | grep ALLOWED_HOSTS
```

### PASO 6: REINICIAR APLICACIÓN
- Ve a la pestaña "Web" en PythonAnywhere
- Haz clic en "Reload"
- Espera 30 segundos

### PASO 7: PROBAR SITIO
- Visita: https://dalej.pythonanywhere.com/

## 🔧 COMANDOS ESPECÍFICOS:

```bash
# 1. VER CONTENIDO ACTUAL
cat multiandamios/settings.py | grep ALLOWED_HOSTS

# 2. EDITAR ARCHIVO
nano multiandamios/settings.py

# 3. VERIFICAR CAMBIO
cat multiandamios/settings.py | grep ALLOWED_HOSTS

# 4. REINICIAR (Panel Web → Reload)
```

## 📋 VERIFICACIÓN DE ÉXITO:

Si el cambio funcionó:
- ✅ No más error 500
- ✅ El sitio carga correctamente
- ✅ Puedes navegar sin errores

## 🚨 SI NANO NO FUNCIONA:

```bash
# Usar vi
vi multiandamios/settings.py

# En vi:
# - Presiona 'i' para insertar
# - Busca y modifica ALLOWED_HOSTS
# - Presiona 'Esc'
# - Escribe ':wq' y presiona Enter
```

## 🎯 ALTERNATIVA - COMANDO DIRECTO:

```bash
# Reemplazar directamente con sed
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py
```

**¡ESTE CAMBIO ES CRÍTICO Y DEBE HACERSE MANUALMENTE!**
