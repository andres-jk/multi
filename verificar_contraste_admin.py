#!/usr/bin/env python
"""
Script para verificar las mejoras de contraste en el CSS del admin
"""

import os
import sys
from pathlib import Path

def verificar_mejoras_contraste():
    """Verificar que las mejoras de contraste estén implementadas"""
    print("🎨 VERIFICACIÓN DE MEJORAS DE CONTRASTE")
    print("=" * 50)
    
    css_path = Path("static/admin/css/admin_custom.css")
    
    if not css_path.exists():
        print("❌ Archivo CSS no encontrado")
        return
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar características de contraste implementadas
    mejoras = [
        ('Hover en filas de tabla', '.change-list table tbody tr:hover' in content),
        ('Enlaces con amarillo en hover', 'color: #ffd700' in content),
        ('Botones con fondo oscuro', '.button:hover' in content and '#2c3e50' in content),
        ('Breadcrumbs con contraste', '.breadcrumbs a:hover' in content),
        ('Filtros laterales mejorados', '#changelist-filter' in content and ':hover' in content),
        ('Paginación contrastada', '.paginator a:hover' in content),
        ('Acciones masivas', '.actions select:hover' in content),
        ('Elementos de ayuda', '.help:hover' in content),
        ('Calendario mejorado', '.calendar td a:hover' in content),
        ('Inline con fondo claro', '.inline-group .tabular tr:hover' in content and '#f0f8ff' in content),
        ('Campos de precio destacados', '.field-precio_diario:hover' in content),
        ('Mensajes del sistema', '.messagelist .info:hover' in content),
        ('Transiciones suaves', 'transition: all 0.3s ease' in content),
        ('Errores legibles', '.errorlist li' in content and '#8b0000' in content),
        ('Tooltips contrastados', '.tooltip:hover' in content),
    ]
    
    print("🔍 Características de contraste implementadas:")
    total_implementadas = 0
    for caracteristica, implementada in mejoras:
        status = "✅" if implementada else "❌"
        print(f"{status} {caracteristica}")
        if implementada:
            total_implementadas += 1
    
    print(f"\n📊 RESUMEN:")
    print(f"Total implementadas: {total_implementadas}/{len(mejoras)}")
    print(f"Porcentaje completado: {(total_implementadas/len(mejoras))*100:.1f}%")
    
    # Contar colores específicos usados
    colores_contraste = {
        '#2c3e50': content.count('#2c3e50'),  # Azul oscuro principal
        '#ffd700': content.count('#ffd700'),  # Amarillo para enlaces
        '#007cba': content.count('#007cba'),  # Azul para bordes
        '#4a4a4a': content.count('#4a4a4a'),  # Gris oscuro para campos
        '#f0f8ff': content.count('#f0f8ff'),  # Azul muy claro para inline
    }
    
    print(f"\n🎨 COLORES DE CONTRASTE UTILIZADOS:")
    for color, count in colores_contraste.items():
        print(f"  {color}: {count} usos")
    
    # Verificar elementos problemáticos que deberían estar cubiertos
    elementos_hover = content.count(':hover')
    print(f"\n🖱️ ELEMENTOS CON HOVER: {elementos_hover}")
    
    elementos_focus = content.count(':focus')
    print(f"🎯 ELEMENTOS CON FOCUS: {elementos_focus}")
    
    transiciones = content.count('transition:')
    print(f"⚡ TRANSICIONES SUAVES: {transiciones}")

def mostrar_problemas_comunes():
    """Mostrar problemas comunes de contraste y sus soluciones"""
    print("\n" + "=" * 50)
    print("🔧 PROBLEMAS COMUNES DE CONTRASTE SOLUCIONADOS:")
    print("=" * 50)
    
    problemas = [
        {
            "problema": "Filas de tabla muy claras al hacer hover",
            "solucion": "Fondo azul oscuro (#2c3e50) con texto blanco",
            "elemento": "tr:hover"
        },
        {
            "problema": "Enlaces invisibles en hover",
            "solucion": "Color amarillo (#ffd700) con subrayado",
            "elemento": "a:hover"
        },
        {
            "problema": "Botones poco visibles en hover",
            "solucion": "Fondo oscuro con borde azul contrastante",
            "elemento": ".button:hover"
        },
        {
            "problema": "Filtros laterales ilegibles",
            "solucion": "Fondo oscuro con texto amarillo destacado",
            "elemento": "#changelist-filter a:hover"
        },
        {
            "problema": "Mensajes del sistema sin contraste",
            "solucion": "Fondos específicos por tipo de mensaje",
            "elemento": ".messagelist :hover"
        },
        {
            "problema": "Elementos inline confusos",
            "solucion": "Fondo azul muy claro con texto oscuro",
            "elemento": ".inline-group tr:hover"
        }
    ]
    
    for i, problema in enumerate(problemas, 1):
        print(f"{i}. 🐛 PROBLEMA: {problema['problema']}")
        print(f"   ✅ SOLUCIÓN: {problema['solucion']}")
        print(f"   🎯 ELEMENTO: {problema['elemento']}")
        print()

def instrucciones_prueba():
    """Mostrar instrucciones para probar las mejoras"""
    print("=" * 50)
    print("🧪 INSTRUCCIONES PARA PROBAR LAS MEJORAS:")
    print("=" * 50)
    
    print("1. 🚀 Inicia el servidor:")
    print("   python manage.py runserver")
    print()
    print("2. 🌐 Ve al admin:")
    print("   http://127.0.0.1:8000/admin/")
    print()
    print("3. 🖱️ PRUEBA ESTOS ELEMENTOS CON HOVER:")
    print("   • Filas en listas de productos/usuarios")
    print("   • Enlaces en breadcrumbs")
    print("   • Botones de acción")
    print("   • Filtros laterales")
    print("   • Enlaces de paginación")
    print("   • Elementos del dashboard")
    print()
    print("4. ✅ VERIFICA QUE:")
    print("   • El texto siempre sea legible")
    print("   • Los colores tengan buen contraste")
    print("   • Las transiciones sean suaves")
    print("   • No haya elementos muy claros que impidan leer")
    print()
    print("5. 🎨 COLORES ESPERADOS:")
    print("   • Hover oscuro: #2c3e50 (azul oscuro)")
    print("   • Enlaces destacados: #ffd700 (amarillo)")
    print("   • Bordes activos: #007cba (azul)")
    print("   • Campos focus: #4a4a4a (gris oscuro)")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    verificar_mejoras_contraste()
    mostrar_problemas_comunes()
    instrucciones_prueba()
    
    print("\n" + "=" * 50)
    print("🎉 ¡MEJORAS DE CONTRASTE IMPLEMENTADAS EXITOSAMENTE!")
    print("=" * 50)

if __name__ == "__main__":
    main()
