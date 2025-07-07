===================================================================
SOLUCIÓN PARA CONFLICTO DE MERGE EN PYTHONANYWHERE
===================================================================

🚨 PROBLEMA: Conflicto con db.sqlite3 al hacer git pull

🔧 SOLUCIÓN PASO A PASO:

1. RESPALDAR LA BASE DE DATOS ACTUAL:
   cp db.sqlite3 db.sqlite3.backup

2. HACER STASH DE LOS CAMBIOS LOCALES:
   git stash

3. ACTUALIZAR CÓDIGO:
   git pull origin main

4. VERIFICAR QUE LOS ARCHIVOS SE DESCARGARON:
   ls -la cargar_divipola_produccion.py
   ls -la verificar_api_divipola.py
   ls -la test_divipola_completo.py

5. CARGAR DATOS DIVIPOLA:
   python3.10 cargar_divipola_produccion.py

6. VERIFICAR API:
   python3.10 verificar_api_divipola.py

7. EJECUTAR TESTS:
   python3.10 test_divipola_completo.py

8. ACTUALIZAR ARCHIVOS ESTÁTICOS:
   python3.10 manage.py collectstatic --clear --noinput

9. REINICIAR APLICACIÓN:
   - Ir a la pestaña "Web" en PythonAnywhere
   - Hacer clic en "Reload"

🔍 VERIFICACIÓN:
Si los archivos no aparecen después del git pull, ejecuta:
   git status
   git log --oneline -5

💡 ALTERNATIVA SI PERSISTEN PROBLEMAS:
Si git stash no funciona, puedes forzar la actualización:
   git reset --hard origin/main

⚠️ NOTA: git reset --hard eliminará todos los cambios locales,
pero como ya tienes el backup de la base de datos, es seguro.

✅ RESULTADO ESPERADO:
Después de estos pasos, el sistema de checkout funcionará
correctamente con departamentos y municipios.
