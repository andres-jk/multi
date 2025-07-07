# 🚨 ERROR CRITICAL IDENTIFICADO - SOLUCIÓN INMEDIATA

## ❌ PROBLEMA:
```
DisallowedHost at /
Invalid HTTP_HOST header: 'dalej.pythonanywhere.com'. 
You may need to add 'dalej.pythonanywhere.com' to ALLOWED_HOSTS.
```

## ✅ SOLUCIÓN INMEDIATA:

### PASO 1: EDITAR SETTINGS.PY

```bash
# En PythonAnywhere, ejecuta:
nano multiandamios/settings.py
```

### PASO 2: BUSCAR Y CAMBIAR ALLOWED_HOSTS

Busca esta línea:
```python
ALLOWED_HOSTS = []
```

O esta línea:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### PASO 3: CAMBIAR A:

```python
ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']
```

### PASO 4: GUARDAR Y SALIR

- Presiona `Ctrl + X`
- Presiona `Y`
- Presiona `Enter`

### PASO 5: REINICIAR APLICACIÓN

- Ve a la pestaña "Web" en PythonAnywhere
- Haz clic en "Reload"

## 🎯 COMANDOS COMPLETOS:

```bash
# 1. EDITAR SETTINGS
nano multiandamios/settings.py

# 2. CAMBIAR ALLOWED_HOSTS (ver arriba)

# 3. GUARDAR: Ctrl + X, Y, Enter

# 4. REINICIAR APLICACIÓN (Panel Web → Reload)

# 5. PROBAR SITIO
# https://dalej.pythonanywhere.com/
```

## 📋 VERIFICACIÓN:

Después de hacer el cambio:
- ✅ El sitio debe cargar sin errores
- ✅ Puedes acceder a https://dalej.pythonanywhere.com/
- ✅ Puedes acceder a https://dalej.pythonanywhere.com/checkout/

## 🔧 ALTERNATIVA SI NO FUNCIONA NANO:

```bash
# Usar vi en lugar de nano
vi multiandamios/settings.py

# En vi:
# - Presiona 'i' para insertar
# - Modifica ALLOWED_HOSTS
# - Presiona 'Esc'
# - Escribe ':wq' y presiona Enter
```

**¡ESTE ES EL PROBLEMA PRINCIPAL! Una vez solucionado, el sitio funcionará correctamente.**
