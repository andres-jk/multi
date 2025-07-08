# 🔧 SOLUCIÓN PARA CONFLICTO DE ARCHIVOS ESTÁTICOS

## 📋 COMANDOS PARA EJECUTAR EN PYTHONANYWHERE:

### 1. LIMPIAR ARCHIVOS ESTÁTICOS CONFLICTIVOS

```bash
# Eliminar archivos estáticos que causan conflicto
rm -rf staticfiles/admin/css/vendor/select2/LICENSE-SELECT2.md
rm -rf staticfiles/admin/js/vendor/select2/LICENSE.md
rm -rf staticfiles/css/entregas.css
rm -rf staticfiles/css/estilos.css
rm -rf staticfiles/css/theme-colors.css
rm -rf staticfiles/test_css_admin.html

# O eliminar toda la carpeta staticfiles y regenerarla
rm -rf staticfiles/
```

### 2. ACTUALIZAR CÓDIGO DESDE GITHUB

```bash
# Ahora sí hacer pull
git pull origin main

# Verificar que se descargaron los archivos móviles
ls -la static/css/ | grep mobile
ls -la static/js/ | grep mobile
ls -la templates/ | grep mobile
```

### 3. REGENERAR ARCHIVOS ESTÁTICOS

```bash
# Generar nuevos archivos estáticos con los móviles incluidos
python3.10 manage.py collectstatic --noinput

# Verificar que se copiaron correctamente
ls -la staticfiles/css/ | grep mobile
ls -la staticfiles/js/ | grep mobile
```

### 4. REINICIAR APLICACIÓN WEB

- Ir al panel web de PythonAnywhere
- Buscar **dalej.pythonanywhere.com**
- Hacer clic en **"Reload"** 
- Esperar confirmación de reinicio

---

## 🚀 COMANDO RESUMIDO (EJECUTAR TODO DE UNA VEZ):

```bash
rm -rf staticfiles/ && git pull origin main && python3.10 manage.py collectstatic --noinput && echo "✅ ¡Interfaz móvil implementada! Reinicia la aplicación web."
```

## 📱 VERIFICAR RESULTADO:

Después de reiniciar, abrir https://dalej.pythonanywhere.com/ en móvil y verificar:
- ✅ Botón hamburguesa (☰) visible en esquina superior derecha
- ✅ Menú se abre al tocarlo
- ✅ Navegación completa en menú lateral
- ✅ Más espacio libre en la pantalla principal

¡El problema de usabilidad móvil estará resuelto!
