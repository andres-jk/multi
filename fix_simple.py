#!/usr/bin/env python3
"""
Corrección ULTRA SIMPLE de ALLOWED_HOSTS
"""

# Leer archivo
with open('multiandamios/settings.py', 'r') as f:
    content = f.read()

# Reemplazar ALLOWED_HOSTS
content = content.replace(
    "ALLOWED_HOSTS = []",
    "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"
)

# También cubrir otras variantes
content = content.replace(
    'ALLOWED_HOSTS = ["localhost", "127.0.0.1"]',
    "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"
)

content = content.replace(
    "ALLOWED_HOSTS = ['localhost', '127.0.0.1']",
    "ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']"
)

# Escribir archivo
with open('multiandamios/settings.py', 'w') as f:
    f.write(content)

print("✅ ALLOWED_HOSTS corregido")
print("🚀 Reinicia la aplicación web ahora (Panel Web → Reload)")
print("🌐 Después visita: https://dalej.pythonanywhere.com/")
