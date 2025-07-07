#!/usr/bin/env python
"""
SCRIPT COMPLETO PARA CARGAR DIVIPOLA EN PYTHONANYWHERE
"""

print("=== SCRIPT COMPLETO PARA CARGAR DIVIPOLA EN PYTHONANYWHERE ===")
print()
print("📋 INSTRUCCIONES PASO A PASO:")
print()
print("1. Subir archivos al repositorio:")
print("   - Ejecutar en local: git add .")
print("   - Ejecutar en local: git commit -m 'Agregar scripts para cargar DIVIPOLA en producción'")
print("   - Ejecutar en local: git push origin main")
print()
print("2. Actualizar código en PythonAnywhere:")
print("   - Abrir consola Bash en PythonAnywhere")
print("   - cd /home/tu-usuario/multiandamios")
print("   - git pull origin main")
print()
print("3. Cargar datos DIVIPOLA:")
print("   - python3.10 cargar_divipola_produccion.py")
print()
print("4. Verificar API:")
print("   - python3.10 verificar_api_divipola.py")
print()
print("5. Reiniciar aplicación web:")
print("   - Ir a la pestaña 'Web' en PythonAnywhere")
print("   - Hacer clic en 'Reload' para reiniciar la aplicación")
print()
print("6. Verificar en el navegador:")
print("   - Ir a tu sitio web")
print("   - Probar el proceso de pedidos")
print("   - Verificar que se cargan los departamentos y municipios")
print()
print("🔧 COMANDOS ADICIONALES SI HAY PROBLEMAS:")
print()
print("- Si hay errores de migración:")
print("  python3.10 manage.py makemigrations")
print("  python3.10 manage.py migrate")
print()
print("- Si hay problemas con archivos estáticos:")
print("  python3.10 manage.py collectstatic --clear --noinput")
print()
print("- Para verificar la base de datos:")
print("  python3.10 manage.py shell")
print("  >>> from usuarios.models import Departamento, Municipio")
print("  >>> print('Departamentos:', Departamento.objects.count())")
print("  >>> print('Municipios:', Municipio.objects.count())")
print()
print("🌐 ENDPOINTS DIVIPOLA A PROBAR:")
print()
print("- Departamentos: https://tu-sitio.pythonanywhere.com/usuarios/api/departamentos/")
print("- Municipios: https://tu-sitio.pythonanywhere.com/usuarios/api/municipios/")
print()
print("✅ VERIFICACIÓN FINAL:")
print("- Login funciona")
print("- Catálogo de productos se ve correctamente")
print("- Carrito funciona")
print("- Proceso de pedidos permite seleccionar departamento y municipio")
print("- Estilos CSS se ven correctamente")
print()

# Crear archivo de comandos para PythonAnywhere
commands_file = """#!/bin/bash
# COMANDOS PARA EJECUTAR EN PYTHONANYWHERE

echo "=== ACTUALIZACIÓN DE CÓDIGO ==="
cd /home/tu-usuario/multiandamios
git pull origin main

echo "=== CARGA DE DATOS DIVIPOLA ==="
python3.10 cargar_divipola_produccion.py

echo "=== VERIFICACIÓN DE API ==="
python3.10 verificar_api_divipola.py

echo "=== COLECCIÓN DE ARCHIVOS ESTÁTICOS ==="
python3.10 manage.py collectstatic --clear --noinput

echo "=== MIGRACIONES ==="
python3.10 manage.py makemigrations
python3.10 manage.py migrate

echo "=== PROCESO COMPLETADO ==="
echo "📝 RECUERDA:"
echo "1. Hacer 'Reload' en la pestaña Web de PythonAnywhere"
echo "2. Probar el sitio web en el navegador"
echo "3. Verificar proceso de pedidos con departamentos/municipios"
"""

with open('comandos_pythonanywhere.sh', 'w') as f:
    f.write(commands_file)

print("📄 Archivo creado: comandos_pythonanywhere.sh")
print("   (Para usar en PythonAnywhere si prefieres un script automático)")
print()
print("🎯 PRÓXIMOS PASOS:")
print("1. Ejecutar en local: git add .")
print("2. Ejecutar en local: git commit -m 'Scripts para DIVIPOLA'")
print("3. Ejecutar en local: git push origin main")
print("4. Seguir las instrucciones en PythonAnywhere")
