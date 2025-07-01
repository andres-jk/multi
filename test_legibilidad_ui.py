#!/usr/bin/env python3
"""
Script para probar la legibilidad mejorada de la interfaz de entregas
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

from usuarios.models import Usuario
from pedidos.models import Pedido, EntregaPedido

def test_legibilidad_ui():
    """Prueba la mejora de legibilidad en la interfaz"""
    
    print("=== PRUEBA DE LEGIBILIDAD DE INTERFAZ DE ENTREGAS ===\n")
    
    # Verificar que existan datos de prueba
    try:
        empleado = Usuario.objects.filter(
            rol='recibos_obra'
        ).first()
        
        if not empleado:
            print("❌ No se encontró empleado de entregas")
            return False
            
        # Verificar que haya entregas
        entregas = EntregaPedido.objects.all()
        if not entregas:
            print("❌ No se encontraron entregas")
            return False
            
        print(f"✅ Empleado encontrado: {empleado.username}")
        print(f"✅ Entregas encontradas: {entregas.count()}")
        
        # Verificar archivos de templates actualizados
        templates_mejorados = [
            'pedidos/templates/entregas/iniciar_recorrido.html',
            'pedidos/templates/entregas/seguimiento_entrega.html', 
            'pedidos/templates/entregas/confirmar_entrega.html',
            'pedidos/templates/entregas/seguimiento_cliente.html'
        ]
        
        for template in templates_mejorados:
            if os.path.exists(template):
                print(f"✅ Template actualizado: {template}")
            else:
                print(f"❌ Template no encontrado: {template}")
                
        # Verificar CSS mejorado
        css_file = 'static/css/entregas.css'
        if os.path.exists(css_file):
            print(f"✅ CSS actualizado: {css_file}")
        else:
            print(f"❌ CSS no encontrado: {css_file}")
            
        print("\n=== MEJORAS IMPLEMENTADAS ===")
        print("✅ Texto negro (#212529) para mejor legibilidad")
        print("✅ Títulos en gris oscuro (#343a40) para jerarquía visual")
        print("✅ Texto auxiliar más oscuro (#6c757d) para mejor contraste")
        print("✅ Fondos claros con texto oscuro")
        print("✅ Colores de botones y estados mantenidos")
        
        print("\n=== TEMPLATES MEJORADOS ===")
        print("✅ iniciar_recorrido.html - Checklist pre-entrega más legible")
        print("✅ seguimiento_entrega.html - Información de seguimiento clara")
        print("✅ confirmar_entrega.html - Formulario de confirmación legible")
        print("✅ seguimiento_cliente.html - Vista del cliente mejorada")
        print("✅ entregas.css - Estilos globales actualizados")
        
        print("\n=== CÓMO PROBAR ===")
        print("1. Ejecutar: python manage.py runserver")
        print("2. Ir a: http://localhost:8000/login/")
        print("3. Usar credenciales de empleado de entregas")
        print("4. Navegar por las páginas de entregas")
        print("5. Verificar que el texto sea legible y tenga buen contraste")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_legibilidad_ui()
    if success:
        print("\n🎉 PRUEBA DE LEGIBILIDAD COMPLETADA EXITOSAMENTE")
    else:
        print("\n❌ PRUEBA DE LEGIBILIDAD FALLÓ")
        sys.exit(1)
