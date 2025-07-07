===================================================================
COMANDOS URGENTES PARA DALEJ - ARCHIVOS NO ENCONTRADOS
===================================================================

🚨 PROBLEMA: Los archivos de DIVIPOLA no se descargaron debido al conflicto de merge

🔧 SOLUCIÓN INMEDIATA:

1. RESPALDAR BASE DE DATOS:
   cp db.sqlite3 db.sqlite3.backup

2. FORZAR ACTUALIZACIÓN DEL REPOSITORIO:
   git reset --hard origin/main

3. VERIFICAR QUE LOS ARCHIVOS AHORA EXISTEN:
   ls -la cargar_divipola_produccion.py
   ls -la verificar_api_divipola.py
   ls -la test_divipola_completo.py

4. SI LOS ARCHIVOS EXISTEN, CONTINUAR:
   python3.10 cargar_divipola_produccion.py
   python3.10 verificar_api_divipola.py
   python3.10 test_divipola_completo.py
   python3.10 manage.py collectstatic --clear --noinput

5. REINICIAR APLICACIÓN WEB:
   - Ir a pestaña "Web" en PythonAnywhere
   - Hacer clic en "Reload"

⚠️ NOTA IMPORTANTE:
git reset --hard eliminará los cambios locales en db.sqlite3,
pero ya hiciste backup, así que es seguro.

✅ DESPUÉS DE ESTOS COMANDOS:
El problema de departamentos y municipios estará solucionado.

🔍 PARA VERIFICAR QUE FUNCIONÓ:
- Ve a tu sitio web
- Intenta hacer un pedido
- Los selectores de departamento y municipio deben funcionar
