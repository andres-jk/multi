#!/usr/bin/env python
"""
Script para verificar la base de datos de usuarios y clientes
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import Usuario, Cliente

print("=== VERIFICACIÓN DE BASE DE DATOS ===")
print(f"Total usuarios: {Usuario.objects.count()}")
print(f"Total clientes: {Cliente.objects.count()}")
print(f"Usuarios con rol cliente: {Usuario.objects.filter(rol='cliente').count()}")

# Verificar últimos usuarios
print("\n=== ÚLTIMOS 5 USUARIOS ===")
for usuario in Usuario.objects.order_by('-id')[:5]:
    tiene_cliente = "SÍ" if hasattr(usuario, 'cliente') else "NO"
    print(f"- {usuario.username} (ID: {usuario.id}) - Rol: {usuario.rol} - Tiene cliente: {tiene_cliente}")

# Verificar usuarios sin cliente
usuarios_sin_cliente = Usuario.objects.filter(rol='cliente').exclude(cliente__isnull=False)
print(f"\nUsuarios con rol 'cliente' sin registro de cliente: {usuarios_sin_cliente.count()}")

if usuarios_sin_cliente.exists():
    print("Usuarios sin cliente:")
    for usuario in usuarios_sin_cliente:
        print(f"- {usuario.username} (ID: {usuario.id})")

# Verificar duplicados por username
from django.db.models import Count
duplicados = Usuario.objects.values('username').annotate(count=Count('id')).filter(count__gt=1)
print(f"\nUsuarios duplicados por username: {duplicados.count()}")

for dup in duplicados:
    usuarios_dup = Usuario.objects.filter(username=dup['username'])
    print(f"- Username '{dup['username']}' usado por:")
    for u in usuarios_dup:
        print(f"  * ID: {u.id}, Email: {u.email}, Tiene cliente: {'SÍ' if hasattr(u, 'cliente') else 'NO'}")
