# 🚨 DALEJ: SOLUCIÓN DE EMERGENCIA - ALLOWED_HOSTS

## ❌ PROBLEMA CRÍTICO:
El error `DisallowedHost` persiste después de múltiples intentos. El archivo `settings.py` no se está modificando correctamente.

## 🚀 SOLUCIÓN DE EMERGENCIA:

### MÉTODO 1: VERIFICAR UBICACIÓN DEL ARCHIVO
```bash
# Verificar si estás en el directorio correcto
pwd
ls -la | grep manage.py

# Verificar si settings.py existe
ls -la multiandamios/settings.py
```

### MÉTODO 2: MOSTRAR CONTENIDO ACTUAL
```bash
# Ver el contenido completo de ALLOWED_HOSTS
cat multiandamios/settings.py | grep -n ALLOWED_HOSTS

# Ver las líneas alrededor de ALLOWED_HOSTS
grep -n -A 3 -B 3 "ALLOWED_HOSTS" multiandamios/settings.py
```

### MÉTODO 3: COMANDO DIRECTO CON SED
```bash
# Crear backup
cp multiandamios/settings.py multiandamios/settings.py.backup

# Reemplazar ALLOWED_HOSTS = [] con la configuración correcta
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py

# Verificar el cambio
grep "ALLOWED_HOSTS" multiandamios/settings.py
```

### MÉTODO 4: USANDO PYTHON PARA EDITAR
```bash
# Ejecutar este comando Python
python3.10 -c "
import re
with open('multiandamios/settings.py', 'r') as f:
    content = f.read()

# Reemplazar ALLOWED_HOSTS
content = re.sub(r'ALLOWED_HOSTS = \[\]', \"ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']\", content)

with open('multiandamios/settings.py', 'w') as f:
    f.write(content)

print('ALLOWED_HOSTS actualizado')
"

# Verificar el cambio
grep "ALLOWED_HOSTS" multiandamios/settings.py
```

### MÉTODO 5: CREAR NUEVO ARCHIVO SETTINGS
```bash
# Si todo falla, crear un nuevo archivo settings con la configuración correcta
cp multiandamios/settings.py multiandamios/settings.py.original

# Agregar la línea correcta al final del archivo
echo "" >> multiandamios/settings.py
echo "# Configuración correcta para PythonAnywhere" >> multiandamios/settings.py
echo "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']" >> multiandamios/settings.py
```

## 🔧 COMANDOS EN ORDEN DE PRIORIDAD:

```bash
# 1. VERIFICAR UBICACIÓN
pwd
ls -la manage.py

# 2. VER CONTENIDO ACTUAL
grep -n "ALLOWED_HOSTS" multiandamios/settings.py

# 3. MÉTODO DIRECTO CON SED
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py

# 4. VERIFICAR CAMBIO
grep "ALLOWED_HOSTS" multiandamios/settings.py

# 5. REINICIAR APLICACIÓN (Panel Web → Reload)
```

## 📋 VERIFICACIÓN OBLIGATORIA:

Después de cualquier cambio, DEBES ver esta línea:
```python
ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']
```

## 🎯 RESULTADO ESPERADO:

Una vez corregido:
- ✅ No más error 500
- ✅ El sitio carga en https://dalej.pythonanywhere.com/
- ✅ Puedes acceder a todas las páginas

**¡EJECUTA LOS COMANDOS EN ORDEN HASTA QUE FUNCIONE!**
