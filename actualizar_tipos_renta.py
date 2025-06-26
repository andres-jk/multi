#!/usr/bin/env python
"""
Script para actualizar productos existentes al nuevo sistema de tipo_renta
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from productos.models import Producto

def actualizar_tipos_renta():
    """Actualiza los tipos de renta a los nuevos valores permitidos"""
    print("🔧 Actualizando tipos de renta de productos...")
    
    productos = Producto.objects.all()
    productos_actualizados = 0
    
    for producto in productos:
        tipo_original = producto.tipo_renta
        
        # Normalizar tipo de renta a los nuevos valores permitidos
        if tipo_original.lower() in ['mes', 'mensual', 'monthly']:
            nuevo_tipo = 'mensual'
        elif tipo_original.lower() in ['semana', 'semanal', 'weekly']:
            nuevo_tipo = 'semanal'
        else:
            # Por defecto, asignar mensual
            nuevo_tipo = 'mensual'
            print(f"⚠️  Producto '{producto.nombre}': tipo '{tipo_original}' → 'mensual' (por defecto)")
        
        if producto.tipo_renta != nuevo_tipo:
            producto.tipo_renta = nuevo_tipo
            producto.save()
            productos_actualizados += 1
            print(f"✅ Producto '{producto.nombre}': '{tipo_original}' → '{nuevo_tipo}'")
    
    print(f"\n📊 Resumen:")
    print(f"   - Total de productos: {productos.count()}")
    print(f"   - Productos actualizados: {productos_actualizados}")
    print(f"   - Productos con tipo mensual: {Producto.objects.filter(tipo_renta='mensual').count()}")
    print(f"   - Productos con tipo semanal: {Producto.objects.filter(tipo_renta='semanal').count()}")
    
    print("\n🎉 Actualización completada!")

if __name__ == "__main__":
    actualizar_tipos_renta()
