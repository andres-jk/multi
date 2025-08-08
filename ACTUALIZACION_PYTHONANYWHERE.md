# 🚀 ACTUALIZACIÓN PYTHONANYWHERE

## 📋 **CAMBIOS SUBIDOS A GITHUB**

### **✅ Archivos Actualizados:**
- `ejecutar_servidor.bat` - Script para ejecutar servidor en Windows
- `ejecutar_servidor.ps1` - Script PowerShell alternativo  
- `usuarios/migrations/0008_merge_20250808_1145.py` - Migración fusionada
- `db.sqlite3` - Base de datos actualizada
- `manage.py` - Archivo de gestión Django
- `static/estilos.css` - Estilos actualizados
- `usuarios/templates/base.html` - Template base mejorado

---

## 🛠️ **INSTRUCCIONES PARA PYTHONANYWHERE**

### **Paso 1: Actualizar Código**
```bash
# En la consola Bash de PythonAnywhere:
cd ~/multi
git pull origin main
```

### **Paso 2: Aplicar Migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **Paso 3: Recolectar Archivos Estáticos**
```bash
python manage.py collectstatic --noinput
```

### **Paso 4: Verificar Configuración**
```bash
python manage.py check
```

### **Paso 5: Reiniciar Aplicación Web**
- Ve a: **Web → dalej.pythonanywhere.com → Reload**

---

## 🧪 **VERIFICACIONES POST-DESPLIEGUE**

### **1. Verificar Sitio Principal**
- Abrir: `https://dalej.pythonanywhere.com`
- Verificar que carga correctamente
- Probar navegación principal

### **2. Verificar Chatbot**
- Buscar botón en esquina inferior derecha
- Hacer click y verificar que se despliega
- Probar envío de mensajes

### **3. Verificar Responsive (Móviles)**
- Probar en dispositivos móviles
- Verificar que chatbot se adapta
- Verificar que menú funciona

### **4. Verificar Funcionalidades Específicas**
- Sistema de usuarios
- Gestión de productos
- Carrito de compras
- Sistema de pedidos

---

## 🔧 **SI HAY PROBLEMAS**

### **Error de Migraciones:**
```bash
python manage.py showmigrations
python manage.py migrate --fake-initial
```

### **Error de Archivos Estáticos:**
```bash
python manage.py collectstatic --noinput --clear
```

### **Error de Permisos:**
```bash
# Verificar permisos de archivos
ls -la
# Si es necesario, ajustar permisos
chmod +x manage.py
```

### **Error de Base de Datos:**
```bash
# Verificar estado de la BD
python manage.py dbshell
# Salir con: .exit
```

---

## 📊 **RESUMEN DE COMMITS SUBIDOS**

1. **Scripts de Servidor**: Archivos .bat y .ps1 para desarrollo local
2. **Migraciones Fusionadas**: Resolución de conflictos en usuarios
3. **Mejoras de UI**: Chatbot responsive y optimizaciones móviles
4. **Correcciones Generales**: Varios bugs y mejoras menores

---

## ✅ **CHECKLIST FINAL**

- [ ] `git pull origin main` ejecutado en PythonAnywhere
- [ ] Migraciones aplicadas sin errores
- [ ] Archivos estáticos recolectados
- [ ] Aplicación web reiniciada
- [ ] Sitio principal carga correctamente
- [ ] Chatbot funciona en desktop y móvil
- [ ] Todas las funcionalidades principales operativas

---

**🎯 Después de estos pasos, tu sitio en PythonAnywhere estará completamente actualizado con todos los cambios recientes.**
