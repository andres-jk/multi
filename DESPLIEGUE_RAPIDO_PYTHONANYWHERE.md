# 🚀 DESPLIEGUE RÁPIDO EN PYTHONANYWHERE

## ⚡ **OPCIÓN 1: DESPLIEGUE AUTOMÁTICO (RECOMENDADO)**

### **Solo 3 comandos en la consola Bash de PythonAnywhere:**

```bash
# 1. Descargar y ejecutar script automático
wget https://raw.githubusercontent.com/andres-jk/multi/main/deploy_pythonanywhere_completo.sh && chmod +x deploy_pythonanywhere_completo.sh && ./deploy_pythonanywhere_completo.sh

# 2. Configurar en la pestaña Web de PythonAnywhere:
# - Source code: /home/TUUSUARIO/multi
# - Working directory: /home/TUUSUARIO/multi  
# - WSGI file: usar el contenido de wsgi_pythonanywhere.py
# - Static files: /static/ -> /home/TUUSUARIO/multi/staticfiles
# - Media files: /media/ -> /home/TUUSUARIO/multi/media
# - Virtualenv: /home/TUUSUARIO/multi/venv

# 3. Recargar la aplicación web
```

**⚠️ IMPORTANTE:** Reemplaza `TUUSUARIO` con tu nombre de usuario de PythonAnywhere

---

## 📋 **OPCIÓN 2: PASO A PASO MANUAL**

### **1. En la consola Bash de PythonAnywhere:**
```bash
cd ~
git clone https://github.com/andres-jk/multi.git
cd multi
python3.10 -m venv venv
source venv/bin/activate
pip install django==4.2.23 reportlab pillow
python manage.py migrate --settings=multiandamios.settings_production
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
python manage.py createsuperuser --settings=multiandamios.settings_production
```

### **2. En la pestaña Web de PythonAnywhere:**
- **Add new web app** → Manual configuration → Python 3.10
- **Source code:** `/home/TUUSUARIO/multi`
- **Working directory:** `/home/TUUSUARIO/multi`
- **WSGI configuration:** Copiar contenido de `wsgi_pythonanywhere.py`
- **Static files:** 
  - URL: `/static/` → Directory: `/home/TUUSUARIO/multi/staticfiles`
  - URL: `/media/` → Directory: `/home/TUUSUARIO/multi/media`
- **Virtualenv:** `/home/TUUSUARIO/multi/venv`
- **Reload** la aplicación

---

## 🔐 **CREDENCIALES INICIALES**

```
URL: https://TUUSUARIO.pythonanywhere.com
Admin: https://TUUSUARIO.pythonanywhere.com/admin/
Usuario: admin
Contraseña: admin123
```

**¡Cambia la contraseña inmediatamente después del primer login!**

---

## 🎯 **VERIFICACIÓN RÁPIDA**

Verifica que funcionen estas URLs:
- ✅ https://TUUSUARIO.pythonanywhere.com (Página principal)
- ✅ https://TUUSUARIO.pythonanywhere.com/admin/ (Panel admin)
- ✅ https://TUUSUARIO.pythonanywhere.com/productos/ (Catálogo)

---

## 🔄 **ACTUALIZAR EN EL FUTURO**

```bash
cd ~/multi
git pull origin main
source venv/bin/activate
python manage.py migrate --settings=multiandamios.settings_production
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
```

Luego **Reload** en la pestaña Web.

---

## 🆘 **SOLUCIÓN RÁPIDA DE PROBLEMAS**

### **Error 500:**
```bash
cd ~/multi
source venv/bin/activate
python manage.py check --settings=multiandamios.settings_production
```

### **Archivos estáticos no cargan:**
```bash
cd ~/multi
source venv/bin/activate
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
```

### **Error de base de datos:**
```bash
cd ~/multi
source venv/bin/activate
python manage.py migrate --settings=multiandamios.settings_production
```

---

## ✅ **¡LISTO!**

Con estos pasos tu aplicación MultiAndamios estará funcionando perfectamente en PythonAnywhere. 

**🎉 ¡Tu proyecto está en vivo!** 🚀
