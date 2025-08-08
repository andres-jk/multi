# 🚨 SOLUCIÓN PARA CONFLICTOS EN PYTHONANYWHERE

## ⚠️ **PROBLEMA DETECTADO**
Hay cambios locales en PythonAnywhere que entran en conflicto con GitHub:
- `db.sqlite3` (base de datos)
- `multiandamios/settings.py` (configuración)

---

## 🔧 **SOLUCIÓN PASO A PASO**

### **OPCIÓN A: MANTENER CAMBIOS LOCALES (RECOMENDADO)**

```bash
# 1. Ir al directorio del proyecto
cd ~/multi

# 2. Ver qué archivos tienen cambios
git status

# 3. Hacer stash de los cambios locales (guardarlos temporalmente)
git stash push -m "Cambios locales antes de actualizar"

# 4. Actualizar desde GitHub
git pull origin main

# 5. Aplicar migraciones
python manage.py migrate

# 6. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 7. Si quieres recuperar algunos cambios locales específicos:
git stash list
# git stash apply stash@{0}  # Solo si es necesario

echo "✅ ACTUALIZACIÓN COMPLETADA - Ve a Web > Reload"
```

### **OPCIÓN B: COMANDO ULTRA-RÁPIDO**

```bash
cd ~/multi && git stash && git pull origin main && python manage.py migrate && python manage.py collectstatic --noinput && echo "✅ ACTUALIZACIÓN COMPLETADA - Ve a Web > Reload"
```

---

## 🔍 **EXPLICACIÓN DE LOS ARCHIVOS EN CONFLICTO**

### **`db.sqlite3`**
- Es la base de datos local de PythonAnywhere
- **MANTENER LOCAL** (no sobrescribir con GitHub)
- Contiene todos los datos de producción

### **`multiandamios/settings.py`**
- Puede tener configuraciones específicas de PythonAnywhere
- **REVISAR** después de la actualización si es necesario

---

## ✅ **DESPUÉS DE LA ACTUALIZACIÓN**

### **1. Reiniciar Aplicación**
- Ve al Dashboard de PythonAnywhere
- Web → dalej.pythonanywhere.com
- Click **"Reload"**

### **2. Verificar Funcionamiento**
- https://dalej.pythonanywhere.com
- Chatbot debe funcionar
- Dimensiones móviles corregidas
- Menú responsivo

### **3. Si hay problemas con settings.py**
```bash
# Ver diferencias en configuración
cd ~/multi
git diff HEAD~1 multiandamios/settings.py

# Si necesitas aplicar cambios específicos manualmente
nano multiandamios/settings.py
```

---

## 🆘 **SI ALGO SALE MAL**

### **Restaurar estado anterior:**
```bash
cd ~/multi
git reset --hard HEAD~1
cp db.sqlite3.backup.[FECHA] db.sqlite3
```

### **Ver logs de error:**
```bash
tail -f /var/log/dalej.pythonanywhere.com.error.log
```

---

## 🎯 **COMANDO FINAL RECOMENDADO**

**Ejecuta esto en la consola de PythonAnywhere:**

```bash
cd ~/multi && echo "Guardando cambios locales..." && git stash push -m "Cambios locales $(date)" && echo "Actualizando desde GitHub..." && git pull origin main && echo "Aplicando migraciones..." && python manage.py migrate && echo "Recolectando archivos estáticos..." && python manage.py collectstatic --noinput && echo "✅ ACTUALIZACIÓN COMPLETADA - Ve a Web > Reload dalej.pythonanywhere.com"
```

**¡Esta solución mantendrá tu base de datos segura y aplicará todas las mejoras!** 🚀
