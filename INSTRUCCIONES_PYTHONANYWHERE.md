# 🚀 GUÍA COMPLETA PARA DESPLEGAR EN PYTHONANYWHERE

## 📋 **INSTRUCCIONES PASO A PASO**

### **FASE 1: PREPARACIÓN EN PYTHONANYWHERE**

#### 1️⃣ **Acceder a PythonAnywhere**
- Ve a https://www.pythonanywhere.com
- Inicia sesión en tu cuenta
- Ve al Dashboard

#### 2️⃣ **Abrir Consola Bash**
- Click en "Consoles" en el dashboard
- Click en "Bash" para abrir una nueva consola

---

### **FASE 2: EJECUTAR SCRIPT DE DESPLIEGUE**

#### 3️⃣ **Descargar y ejecutar el script**
```bash
# Descargar el script de despliegue
wget https://raw.githubusercontent.com/andres-jk/multi/main/deploy_pythonanywhere_completo.sh

# Hacer ejecutable
chmod +x deploy_pythonanywhere_completo.sh

# Ejecutar el script
./deploy_pythonanywhere_completo.sh
```

**⚠️ IMPORTANTE:** Si tienes un nombre de usuario diferente a "dalej", edita el script antes de ejecutarlo:
```bash
# Editar el script para cambiar el nombre de usuario
nano deploy_pythonanywhere_completo.sh
# Cambiar todas las ocurrencias de "dalej" por tu nombre de usuario
```

---

### **FASE 3: CONFIGURACIÓN MANUAL EN PYTHONANYWHERE**

#### 4️⃣ **Configurar la aplicación Web**
1. Ve a la pestaña **"Web"** en tu dashboard
2. Si no tienes una app web, click **"Add a new web app"**
3. Selecciona **"Manual configuration"** 
4. Selecciona **Python 3.10**

#### 5️⃣ **Configurar rutas del proyecto**
En la sección **"Code"**:
- **Source code:** `/home/TUUSUARIO/multi`
- **Working directory:** `/home/TUUSUARIO/multi`

#### 6️⃣ **Configurar WSGI**
1. Click en el enlace del archivo WSGI
2. Reemplaza todo el contenido con:
```python
"""
Configuración WSGI para MultiAndamios en PythonAnywhere
"""

import os
import sys

# Configurar el path del proyecto
project_home = '/home/TUUSUARIO/multi'  # Cambiar TUUSUARIO
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activar el entorno virtual
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings_production')

# Importar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 7️⃣ **Configurar archivos estáticos**
En la sección **"Static files"**:

**Primera entrada:**
- **URL:** `/static/`
- **Directory:** `/home/TUUSUARIO/multi/staticfiles`

**Segunda entrada:**
- **URL:** `/media/`
- **Directory:** `/home/TUUSUARIO/multi/media`

#### 8️⃣ **Configurar entorno virtual**
En la sección **"Virtualenv"**:
- **Virtualenv:** `/home/TUUSUARIO/multi/venv`

---

### **FASE 4: ACTIVACIÓN Y VERIFICACIÓN**

#### 9️⃣ **Recargar la aplicación**
1. Scroll hasta arriba en la pestaña Web
2. Click el botón verde **"Reload"**
3. Espera a que aparezca "Web app reloaded"

#### 🔟 **Verificar funcionamiento**
1. Click en el enlace de tu aplicación (ej: https://dalej.pythonanywhere.com)
2. Deberías ver la página de inicio de MultiAndamios

---

### **FASE 5: CONFIGURACIÓN DE ADMINISTRADOR**

#### 1️⃣1️⃣ **Acceder al admin**
1. Ve a: `https://TUUSUARIO.pythonanywhere.com/admin/`
2. Usa las credenciales:
   - **Usuario:** admin
   - **Contraseña:** admin123

#### 1️⃣2️⃣ **Cambiar contraseña del admin**
1. Una vez en el admin, click en "Users"
2. Click en "admin"
3. Cambia la contraseña por una segura
4. Guarda los cambios

---

## 🔧 **COMANDOS ALTERNATIVOS (SI EL SCRIPT FALLA)**

### **Despliegue manual paso a paso:**

```bash
# 1. Clonar repositorio
cd ~
git clone https://github.com/andres-jk/multi.git
cd multi

# 2. Crear entorno virtual
python3.10 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install django==4.2.23 reportlab pillow

# 4. Crear settings de producción
cp multiandamios/settings.py multiandamios/settings_production.py

# 5. Editar settings_production.py
nano multiandamios/settings_production.py
# Cambiar:
# DEBUG = False
# ALLOWED_HOSTS = ['TUUSUARIO.pythonanywhere.com']

# 6. Aplicar migraciones
python manage.py migrate --settings=multiandamios.settings_production

# 7. Recopilar archivos estáticos
python manage.py collectstatic --noinput --settings=multiandamios.settings_production

# 8. Crear superusuario
python manage.py createsuperuser --settings=multiandamios.settings_production
```

---

## ❗ **SOLUCIÓN DE PROBLEMAS COMUNES**

### **Error 1: "ImportError"**
```bash
# Verificar que el entorno virtual esté activado
source ~/multi/venv/bin/activate
pip list
```

### **Error 2: "DisallowedHost"**
- Verificar que tu dominio esté en ALLOWED_HOSTS en settings_production.py

### **Error 3: "Static files not found"**
```bash
# Recopilar archivos estáticos nuevamente
cd ~/multi
source venv/bin/activate
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
```

### **Error 4: "Database error"**
```bash
# Aplicar migraciones
cd ~/multi
source venv/bin/activate
python manage.py migrate --settings=multiandamios.settings_production
```

---

## ✅ **VERIFICACIÓN FINAL**

Una vez completado el despliegue, verifica que funcionen:

1. **Página de inicio:** https://TUUSUARIO.pythonanywhere.com
2. **Admin panel:** https://TUUSUARIO.pythonanywhere.com/admin/
3. **Catálogo:** https://TUUSUARIO.pythonanywhere.com/productos/
4. **Login:** https://TUUSUARIO.pythonanywhere.com/login/
5. **Registro:** https://TUUSUARIO.pythonanywhere.com/registro/

---

## 🎉 **¡DESPLIEGUE COMPLETADO!**

Si siguiste todos los pasos correctamente, tu aplicación MultiAndamios debería estar funcionando perfectamente en PythonAnywhere.

**URLs importantes:**
- **Aplicación:** https://TUUSUARIO.pythonanywhere.com
- **Admin:** https://TUUSUARIO.pythonanywhere.com/admin/
- **Dashboard PythonAnywhere:** https://www.pythonanywhere.com/user/TUUSUARIO/

**Credenciales iniciales:**
- **Usuario admin:** admin
- **Contraseña:** admin123 (¡Cámbiala inmediatamente!)

---

## 🔄 **ACTUALIZACIONES FUTURAS**

Para actualizar la aplicación con nuevos cambios:

```bash
cd ~/multi
git pull origin main
source venv/bin/activate
python manage.py migrate --settings=multiandamios.settings_production
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
```

Luego recarga la aplicación web desde el dashboard de PythonAnywhere.
