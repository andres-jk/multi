# 🚨 COMANDOS CORREGIDOS PARA DALEJ

## ❌ PROBLEMA:
- `git pull origin main` está mal escrito
- Los archivos de diagnóstico no se han descargado

## ✅ SOLUCIÓN INMEDIATA:

### COMANDOS CORRECTOS:

```bash
# 1. DESCARGAR ARCHIVOS (COMANDO CORRECTO)
git pull origin main
# (Sin espacio entre "origin" y "main")

# 2. VERIFICAR QUE APARECIERON
ls -la | grep diagnostico

# 3. SI NO APARECEN, FORZAR DESCARGA
git fetch --all
git reset --hard origin/main

# 4. VERIFICAR OTRA VEZ
ls -la | grep diagnostico
```

### COMANDOS ALTERNATIVOS SI NO FUNCIONA:

```bash
# MÉTODO 1: Fetch y reset
git fetch --all
git reset --hard origin/main
git clean -fd

# MÉTODO 2: Verificar conexión
git remote -v
git status

# MÉTODO 3: Pull forzado
git pull --rebase origin main
```

### VERIFICACIÓN RÁPIDA SIN ARCHIVOS:

```bash
# PROBAR DIRECTAMENTE EN EL NAVEGADOR
# Visitar: https://dalej.pythonanywhere.com/checkout/

# VERIFICAR DATOS EN DJANGO
python3.10 manage.py shell -c "
from usuarios.models_divipola import Departamento, Municipio
print('Departamentos:', Departamento.objects.count())
print('Municipios:', Municipio.objects.count())
"
```

## 🎯 PRIORIDAD ALTA - PROBAR EL SITIO:

**¡IMPORTANTE!** Antes de diagnosticar más, prueba el sitio web:

1. **Reinicia la aplicación** (Panel Web → Reload)
2. **Visita**: https://dalej.pythonanywhere.com/checkout/
3. **Verifica**: Si los selectores de departamento y municipio funcionan

## 📋 COMANDOS EN ORDEN:

```bash
# 1. COMANDO CORRECTO
git pull origin main

# 2. SI FALLA, USAR ESTO
git fetch --all
git reset --hard origin/main

# 3. VERIFICAR ARCHIVOS
ls -la | grep -E "(diagnostico|verificar)"

# 4. REINICIAR APLICACIÓN
# (Panel Web → Reload)

# 5. PROBAR SITIO
# https://dalej.pythonanywhere.com/checkout/
```

¡Usa `git pull origin main` SIN ESPACIO!
