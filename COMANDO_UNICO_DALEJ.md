===================================================================
COMANDO ÚNICO PARA DALEJ - EJECUTAR ESTE COMANDO AHORA MISMO
===================================================================

🚨 EJECUTA EXACTAMENTE ESTO EN PYTHONANYWHERE:

git reset --hard origin/main

📋 DESPUÉS DEL COMANDO, VERIFICA:

ls -la cargar_divipola_produccion.py

SI VES EL ARCHIVO, EJECUTA:

python3.10 cargar_divipola_produccion.py

🔍 SI NO VES EL ARCHIVO, EJECUTA:

git pull origin main
git status
git log --oneline -3

⚠️ EL PROBLEMA:
Los archivos de DIVIPOLA están en el repositorio remoto pero no se han descargado
a tu servidor debido al conflicto con db.sqlite3.

✅ SOLUCIÓN:
git reset --hard origin/main FORZARÁ la descarga de TODOS los archivos.

🎯 DESPUÉS DE QUE APAREZCAN LOS ARCHIVOS:
1. python3.10 cargar_divipola_produccion.py
2. python3.10 verificar_api_divipola.py
3. python3.10 manage.py collectstatic --noinput
4. Reload de la aplicación web

💡 ALTERNATIVA SI PERSISTE:
git fetch origin
git reset --hard origin/main

🚀 SOLO NECESITAS EJECUTAR:
git reset --hard origin/main

¡Y los archivos aparecerán!
