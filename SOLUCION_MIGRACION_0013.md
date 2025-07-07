# 🔧 SOLUCIONANDO CONFLICTO DE MIGRACIÓN 0013

## ❌ PROBLEMA IDENTIFICADO:
```
sqlite3.OperationalError: duplicate column name: fecha_entrega
Applying pedidos.0013_entregapedido_fecha_entrega_and_more...
```

**La columna `fecha_entrega` ya existe, pero la migración 0013 intenta crearla de nuevo.**

## 🚀 SOLUCIÓN PASO A PASO:

### OPCIÓN 1: Marcar migración como aplicada (RECOMENDADO)

```bash
# 1. Marcar la migración problemática como ya aplicada
python manage.py migrate pedidos 0013 --fake

# 2. Continuar con las migraciones restantes
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Recolectar archivos estáticos actualizados
python manage.py collectstatic --clear --noinput
```

### OPCIÓN 2: Ver estado y aplicar selectivamente

```bash
# 1. Ver estado de todas las migraciones
python manage.py showmigrations

# 2. Marcar migraciones específicas como fake
python manage.py migrate pedidos 0013 --fake
python manage.py migrate pedidos 0014 --fake  # Si existe

# 3. Continuar con migraciones
python manage.py migrate
```

### OPCIÓN 3: Base de datos limpia (si persisten problemas)

```bash
# 1. Respaldar base actual
mv db.sqlite3 db.sqlite3.backup.conflicted

# 2. Crear base limpia
python manage.py migrate

# 3. Crear superusuario
python manage.py createsuperuser

# 4. Archivos estáticos
python manage.py collectstatic --clear --noinput
```

## 🎯 DESPUÉS DE LA SOLUCIÓN:

1. **Reload** en PythonAnywhere
2. **Visitar** https://dalej.pythonanywhere.com
3. **¡Ver tu aplicación completa funcionando!**

## 📋 RESULTADO ESPERADO:

- ✅ **Base de datos** completamente migrada
- ✅ **Todas las apps** funcionando
- ✅ **Archivos estáticos** actualizados
- ✅ **Aspecto visual** correcto
- ✅ **Funcionalidad completa** restaurada

## 🔧 COMANDO RÁPIDO:

```bash
python manage.py migrate pedidos 0013 --fake && python manage.py migrate && python manage.py createsuperuser && python manage.py collectstatic --clear --noinput
```

¡Ejecuta la **OPCIÓN 1** y tu aplicación estará lista! 🚀
