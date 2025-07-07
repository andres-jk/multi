===================================================================
COMANDOS EXACTOS PARA DALEJ - EJECUTAR UNO POR UNO
===================================================================

🚨 PROBLEMA: Los archivos Python no se descargaron porque el conflicto de merge no se resolvió

✅ SOLUCIÓN PASO A PASO (ejecutar línea por línea):

# Paso 1: Respaldar base de datos
cp db.sqlite3 db.sqlite3.backup

# Paso 2: Mostrar estado actual de git
git status

# Paso 3: Forzar descarga de TODOS los archivos del repositorio
git reset --hard origin/main

# Paso 4: Verificar que los archivos YA EXISTEN
ls -la | grep divipola

# Paso 5: Si los archivos aparecen, ejecutar:
python3.10 cargar_divipola_produccion.py

# Paso 6: Verificar API
python3.10 verificar_api_divipola.py

# Paso 7: Ejecutar tests
python3.10 test_divipola_completo.py

# Paso 8: Actualizar archivos estáticos
python3.10 manage.py collectstatic --clear --noinput

# Paso 9: Ve a la pestaña "Web" en PythonAnywhere y haz clic en "Reload"

🔍 DESPUÉS DEL PASO 4:
Si ves archivos como:
- cargar_divipola_produccion.py
- verificar_api_divipola.py
- test_divipola_completo.py

Entonces puedes continuar con los pasos 5-9.

⚠️ SI AÚN NO VES LOS ARCHIVOS:
Ejecuta: git log --oneline -3
Deberías ver commits recientes sobre DIVIPOLA.

✅ RESULTADO FINAL:
El sistema de checkout funcionará con departamentos y municipios.

🎯 PRUEBA FINAL:
- Ve a tu sitio web
- Intenta hacer un pedido
- Selecciona departamento y municipio
- Debe funcionar sin errores
