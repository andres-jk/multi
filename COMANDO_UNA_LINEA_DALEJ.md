# 🚨 COMANDO DE UNA LÍNEA PARA DALEJ

## ERROR ACTUAL:
```
DisallowedHost: 'dalej.pythonanywhere.com'
```

## SOLUCIÓN DE UNA LÍNEA:

```bash
sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']/" multiandamios/settings.py
```

## DESPUÉS DEL COMANDO:

1. **Reinicia la aplicación** (Panel Web → Reload)
2. **Visita**: https://dalej.pythonanywhere.com/
3. **Debería funcionar sin errores**

## VERIFICACIÓN:

```bash
# Verificar que el cambio se aplicó
grep "ALLOWED_HOSTS" multiandamios/settings.py
```

## ALTERNATIVA SI NO FUNCIONA:

```bash
# Comando alternativo
echo "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']" >> multiandamios/settings.py
```

## MANUAL (SI LOS COMANDOS FALLAN):

```bash
# 1. Abrir archivo
nano multiandamios/settings.py

# 2. Buscar: ALLOWED_HOSTS = []
# 3. Cambiar a: ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']
# 4. Guardar: Ctrl + X, Y, Enter
```

¡SOLO EJECUTA EL COMANDO DE UNA LÍNEA Y REINICIA LA APLICACIÓN!
