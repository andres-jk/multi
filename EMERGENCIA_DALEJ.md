# 🚨 COMANDOS DE EMERGENCIA PARA DALEJ

## PROBLEMA: Los archivos más recientes no están en el servidor

### SOLUCIÓN INMEDIATA:

```bash
# 1. FORZAR DESCARGA COMPLETA
git fetch --all
git reset --hard origin/main
git clean -fd

# 2. VERIFICAR QUE LOS ARCHIVOS APARECIERON
ls -la | grep verificacion

# 3. SI SIGUEN FALTANDO, EJECUTAR:
git pull origin main --force

# 4. VERIFICAR ESTADO
python3.10 verificar_estado_basico.py
```

### SI NADA FUNCIONA:

```bash
# ÚLTIMO RECURSO - CLONAR REPOSITORIO FRESCO
cd /home/Dalej
mv multi multi_backup
git clone https://github.com/andres-jk/multi.git
cd multi

# COPIAR BASE DE DATOS
cp ../multi_backup/db.sqlite3 .

# CONTINUAR CON CONFIGURACIÓN
python3.10 verificar_estado_basico.py
```

### VERIFICACIÓN RÁPIDA:

```bash
# VERIFICAR ESTADO ACTUAL
python3.10 verificar_estado_basico.py

# SI DJANGO FUNCIONA, VERIFICAR DIVIPOLA
python3.10 manage.py shell -c "from usuarios.models_divipola import Departamento; print('Departamentos:', Departamento.objects.count())"
```

### COMANDOS PASO A PASO:

```bash
# 1. Verificar estado
pwd
ls -la | head -10

# 2. Forzar actualización
git fetch --all
git reset --hard origin/main

# 3. Verificar archivos
ls -la | grep -E "(verificacion|resumen)"

# 4. Si aparecen archivos, ejecutar:
python3.10 verificacion_final_sistema.py

# 5. Actualizar estáticos
python3.10 manage.py collectstatic --noinput

# 6. Reiniciar aplicación web
```

### ARCHIVOS QUE DEBEN ESTAR PRESENTES:

- ✅ `verificacion_final_sistema.py`
- ✅ `verificar_api_divipola.py`
- ✅ `test_divipola_completo.py`
- ✅ `RESUMEN_EJECUTIVO_DALEJ.md`
- ✅ `INSTRUCCIONES_FINALES_DALEJ.md`

### NOTA IMPORTANTE:

Los archivos están en el repositorio (confirmado). Si no aparecen después de `git reset --hard origin/main`, hay un problema de sincronización que se soluciona con `git fetch --all` primero.

¡Ejecuta los comandos en orden y los archivos aparecerán!
