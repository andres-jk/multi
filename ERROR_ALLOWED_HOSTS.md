===================================================================
ERROR CRÍTICO: ALLOWED_HOSTS EN SETTINGS.PY
===================================================================

🚨 PROBLEMA IDENTIFICADO:
El error muestra que 'dalej.pythonanywhere.com' no está en ALLOWED_HOSTS

❌ ERROR ACTUAL:
DisallowedHost: Invalid HTTP_HOST header: 'dalej.pythonanywhere.com'. 
You may need to add 'dalej.pythonanywhere.com' to ALLOWED_HOSTS.

✅ SOLUCIÓN INMEDIATA:

1. EDITAR EL ARCHIVO SETTINGS.PY:
   nano multiandamios/settings.py

2. BUSCAR LA LÍNEA ALLOWED_HOSTS Y CAMBIARLA A:
   ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']

   O para permitir todos los hosts en producción:
   ALLOWED_HOSTS = ['*']

3. GUARDAR EL ARCHIVO:
   Ctrl + X, luego Y, luego Enter

4. REINICIAR LA APLICACIÓN WEB:
   - Ir a la pestaña "Web" en PythonAnywhere
   - Hacer clic en "Reload"

🔧 EJEMPLO COMPLETO DE ALLOWED_HOSTS:

# En multiandamios/settings.py
ALLOWED_HOSTS = [
    'dalej.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
    '::1',
]

⚠️ ALTERNATIVA RÁPIDA:
Si quieres una solución temporal rápida:
ALLOWED_HOSTS = ['*']

Esto permite TODOS los hosts (útil para desarrollo/testing).

✅ DESPUÉS DE ESTA CORRECCIÓN:
- El sitio web funcionará normalmente
- Podrás acceder a /checkout/ sin errores
- Los departamentos y municipios deberían aparecer

🎯 LUEGO CONTINÚA CON LOS COMANDOS DIVIPOLA:
Una vez que el sitio funcione, ejecuta:
python3.10 cargar_divipola_produccion.py
python3.10 verificar_api_divipola.py
