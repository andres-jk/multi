===================================================================
COMANDOS ESPECÍFICOS PARA EL REPOSITORIO MULTIANDAMIOS
===================================================================

🔧 ESTRUCTURA CORRECTA DEL REPOSITORIO:
- Repositorio: multiandamios
- Ruta en PythonAnywhere: /home/TU-USUARIO/multiandamios
- Archivo WSGI: /home/TU-USUARIO/multi (carpeta del proyecto Django)

📋 COMANDOS EXACTOS PARA EJECUTAR:

1. ABRIR CONSOLA BASH EN PYTHONANYWHERE
   - Ir a la pestaña "Consoles" 
   - Hacer clic en "Bash"

2. NAVEGAR AL REPOSITORIO
   cd /home/TU-USUARIO/multiandamios
   # Reemplaza "TU-USUARIO" por tu usuario real de PythonAnywhere

3. ACTUALIZAR CÓDIGO
   git pull origin main

4. CARGAR DATOS DIVIPOLA
   python3.10 cargar_divipola_produccion.py

5. VERIFICAR API
   python3.10 verificar_api_divipola.py

6. ACTUALIZAR ARCHIVOS ESTÁTICOS
   python3.10 manage.py collectstatic --clear --noinput

7. REINICIAR APLICACIÓN WEB
   - Ir a la pestaña "Web"
   - Hacer clic en el botón "Reload"

🌐 ESTRUCTURA DE RUTAS:
- Repositorio Git: /home/TU-USUARIO/multiandamios/
- Proyecto Django: /home/TU-USUARIO/multi/
- Archivo WSGI apunta a: /home/TU-USUARIO/multi/

✅ VERIFICACIÓN FINAL:
Después de ejecutar todos los comandos, verifica en tu sitio web que:
- Los departamentos aparecen en el selector
- Al seleccionar un departamento, se cargan sus municipios
- El formulario de checkout funciona completamente

🚨 IMPORTANTE:
- Asegúrate de usar TU usuario real de PythonAnywhere
- El archivo WSGI debe apuntar a /home/TU-USUARIO/multi/
- El repositorio está en /home/TU-USUARIO/multiandamios/
