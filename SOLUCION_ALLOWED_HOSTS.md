# SOLUCIÓN: Error DisallowedHost en PythonAnywhere

## El Problema
```
Exception Type: DisallowedHost at /
Exception Value: Invalid HTTP_HOST header: 'dalej.pythonanywhere.com'. You may need to add 'dalej.pythonanywhere.com' to ALLOWED_HOSTS.
```

## Causa
Django requiere que todos los dominios desde los cuales se accede a la aplicación estén explícitamente permitidos en la configuración `ALLOWED_HOSTS` por razones de seguridad.

## Solución Rápida

### Opción 1: Script Automático (Recomendado)
```bash
# En la consola de PythonAnywhere:
cd ~/multi
chmod +x fix_allowed_hosts_error.sh
./fix_allowed_hosts_error.sh
```

### Opción 2: Manual

#### 1. Verificar configuración WSGI
Asegúrate de que el archivo `/var/www/dalej_pythonanywhere_com_wsgi.py` contenga:

```python
import os
import sys

# Configurar el path del proyecto
project_home = '/home/dalej/multi'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activar el entorno virtual
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# IMPORTANTE: Usar settings de producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings_production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 2. Verificar ALLOWED_HOSTS en settings_production.py
El archivo `multiandamios/settings_production.py` debe contener:

```python
ALLOWED_HOSTS = [
    'dalej.pythonanywhere.com',
    'www.dalej.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]
```

#### 3. Aplicar cambios
```bash
cd ~/multi
python manage.py migrate --settings=multiandamios.settings_production
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
```

#### 4. Reiniciar aplicación
- Ve a [tu panel de PythonAnywhere](https://www.pythonanywhere.com/user/dalej/)
- Pestaña "Web"
- Click en "Reload dalej.pythonanywhere.com"

## Verificación
1. Visita: https://dalej.pythonanywhere.com
2. Deberías ver la página de inicio sin errores

## Si el problema persiste

### Verificar logs
1. Ve a PythonAnywhere > Web > Log files
2. Revisa el "error log" para más detalles
3. Busca otros errores que puedan estar ocurriendo

### Comandos de diagnóstico
```bash
cd ~/multi
chmod +x diagnostico_pythonanywhere.sh
./diagnostico_pythonanywhere.sh
```

### Problemas comunes adicionales

#### Error: No module named 'multiandamios'
**Solución:** Verificar que el path del proyecto esté correcto en el WSGI:
```python
project_home = '/home/dalej/multi'  # Debe ser tu directorio correcto
```

#### Error: No such file or directory (WSGI)
**Solución:** Copiar el archivo WSGI al directorio correcto:
```bash
cp ~/multi/wsgi_pythonanywhere.py /var/www/dalej_pythonanywhere_com_wsgi.py
```

#### Error: Base de datos
**Solución:** Aplicar migraciones:
```bash
cd ~/multi
python manage.py migrate --settings=multiandamios.settings_production
```

#### Error: Archivos estáticos
**Solución:** Recolectar archivos estáticos:
```bash
cd ~/multi
python manage.py collectstatic --noinput --settings=multiandamios.settings_production
```

## Configuración final esperada

```
Proyecto: /home/dalej/multi/
WSGI: /var/www/dalej_pythonanywhere_com_wsgi.py
Settings: multiandamios.settings_production
URL: https://dalej.pythonanywhere.com
```

## Contacto
Si sigues teniendo problemas, revisa:
1. Los logs de error en PythonAnywhere
2. Que el entorno virtual esté correctamente configurado
3. Que todos los archivos estén en sus ubicaciones correctas

¡La aplicación debería funcionar correctamente después de seguir estos pasos!
