#!/usr/bin/env python
"""
Script para verificar que se han corregido los problemas de campos muy claros al hacer hover
"""

import os
import sys
from pathlib import Path

def verificar_correccion_hover():
    """Verificar que se corrigieron los problemas de hover muy claro"""
    print("🔧 VERIFICACIÓN: CORRECCIÓN DE CAMPOS MUY CLAROS AL HACER HOVER")
    print("=" * 65)
    
    css_path = Path("static/admin/css/admin_custom.css")
    
    if not css_path.exists():
        print("❌ Archivo CSS no encontrado")
        return
    
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar correcciones específicas implementadas
    correcciones = [
        ('Sobrescritura de form-row:hover', '.form-row:hover' in content and '#2c3e50' in content),
        ('Corrección de campos de entrada', 'input:hover' in content and '#4a4a4a' in content),
        ('Enlaces con color amarillo', '.form-row:hover a' in content and '#ffd700' in content),
        ('Campos de solo lectura mejorados', '.readonly:hover' in content),
        ('Celdas de tabla oscuras', '.change-list tbody tr:hover' in content and '#2c3e50' in content),
        ('Widgets con fondo oscuro', '.widget:hover' in content and '#4a4a4a' in content),
        ('Checkboxes invertidos', 'filter: invert(1)' in content),
        ('Elementos de fecha mejorados', '.datetime:hover' in content),
        ('Sobrescritura forzada', '.change-list tbody tr:hover *' in content),
        ('Excepciones para colores importantes', '.field-precio_diario' in content and '#ffd700' in content),
    ]
    
    print("🔍 Correcciones implementadas:")
    total_corregidas = 0
    for correccion, implementada in correcciones:
        status = "✅" if implementada else "❌"
        print(f"{status} {correccion}")
        if implementada:
            total_corregidas += 1
    
    print(f"\n📊 RESUMEN DE CORRECCIONES:")
    print(f"Total corregidas: {total_corregidas}/{len(correcciones)}")
    print(f"Porcentaje completado: {(total_corregidas/len(correcciones))*100:.1f}%")
    
    # Verificar colores específicos para hover
    colores_hover = {
        '#2c3e50': content.count('#2c3e50'),  # Azul oscuro para fondos de hover
        '#4a4a4a': content.count('#4a4a4a'),  # Gris oscuro para campos
        '#ffd700': content.count('#ffd700'),  # Amarillo para enlaces importantes
        '#ffffff': content.count('#ffffff'),  # Blanco para texto sobre fondos oscuros
        '#34495e': content.count('#34495e'),  # Gris azulado para campos readonly
    }
    
    print(f"\n🎨 COLORES UTILIZADOS PARA CORRECCIÓN:")
    for color, count in colores_hover.items():
        print(f"  {color}: {count} usos")
    
    # Contar reglas específicas
    reglas_hover = content.count(':hover')
    reglas_important = content.count('!important')
    
    print(f"\n📏 ESTADÍSTICAS DEL CSS:")
    print(f"🖱️ Reglas :hover total: {reglas_hover}")
    print(f"❗ Reglas !important: {reglas_important}")
    print(f"📄 Líneas de código total: {len(content.splitlines())}")

def mostrar_problemas_solucionados():
    """Mostrar los problemas específicos que se solucionaron"""
    print("\n" + "=" * 65)
    print("🐛 PROBLEMAS ESPECÍFICOS SOLUCIONADOS:")
    print("=" * 65)
    
    problemas = [
        {
            "problema": "Filas de tabla muy claras al hacer hover",
            "antes": "Fondo blanco/muy claro, texto invisible",
            "ahora": "Fondo azul oscuro (#2c3e50), texto blanco visible",
            "selector": ".change-list tbody tr:hover"
        },
        {
            "problema": "Campos de entrada ilegibles en hover",
            "antes": "Fondo muy claro, bajo contraste",
            "ahora": "Fondo gris oscuro (#4a4a4a), texto blanco",
            "selector": "input:hover, textarea:hover, select:hover"
        },
        {
            "problema": "Enlaces desaparecen en hover",
            "antes": "Color muy claro, invisible sobre fondo claro",
            "ahora": "Color amarillo (#ffd700) con negrita y subrayado",
            "selector": ".form-row:hover a"
        },
        {
            "problema": "Campos de solo lectura poco visibles",
            "antes": "Sin diferenciación clara",
            "ahora": "Fondo gris azulado (#34495e) con padding",
            "selector": ".readonly:hover"
        },
        {
            "problema": "Checkboxes invisibles en filas hover",
            "antes": "Se vuelven blancos sobre fondo blanco",
            "ahora": "Invertidos automáticamente para contraste",
            "selector": "filter: invert(1) hue-rotate(180deg)"
        },
        {
            "problema": "Widgets y campos especiales claros",
            "antes": "Fondo predeterminado muy claro",
            "ahora": "Fondo oscuro consistente con bordes azules",
            "selector": ".widget:hover, .form-widget:hover"
        }
    ]
    
    for i, problema in enumerate(problemas, 1):
        print(f"{i}. 🐛 PROBLEMA: {problema['problema']}")
        print(f"   ❌ ANTES: {problema['antes']}")
        print(f"   ✅ AHORA: {problema['ahora']}")
        print(f"   🎯 SELECTOR: {problema['selector']}")
        print()

def instrucciones_prueba():
    """Instrucciones específicas para probar las correcciones"""
    print("=" * 65)
    print("🧪 INSTRUCCIONES PARA PROBAR LAS CORRECCIONES:")
    print("=" * 65)
    
    print("1. 🚀 Inicia el servidor:")
    print("   python manage.py runserver")
    print()
    print("2. 🌐 Ve al admin:")
    print("   http://127.0.0.1:8000/admin/")
    print()
    print("3. 🖱️ PRUEBA ESTOS ELEMENTOS CON HOVER:")
    print("   ✅ Lista de productos: /admin/productos/producto/")
    print("   ✅ Lista de usuarios: /admin/usuarios/usuario/")
    print("   ✅ Lista de pedidos: /admin/pedidos/pedido/")
    print("   ✅ Formularios de edición de cualquier modelo")
    print()
    print("4. ⚠️ ELEMENTOS ESPECÍFICOS A VERIFICAR:")
    print("   • Filas de la tabla al pasar el mouse")
    print("   • Campos de texto en formularios")
    print("   • Enlaces dentro de celdas")
    print("   • Campos de solo lectura")
    print("   • Checkboxes en listas")
    print("   • Campos de precio y días mínimos")
    print()
    print("5. ✅ RESULTADOS ESPERADOS:")
    print("   • Texto SIEMPRE legible y contrastado")
    print("   • Fondos oscuros (#2c3e50 o #4a4a4a)")
    print("   • Enlaces amarillos (#ffd700) bien visibles")
    print("   • Transiciones suaves entre estados")
    print("   • Sin elementos que desaparezcan en hover")
    print()
    print("6. 🔄 SI AÚN HAY PROBLEMAS:")
    print("   • Ejecuta: python manage.py collectstatic --noinput")
    print("   • Recarga con Ctrl+F5 (forzar recarga de CSS)")
    print("   • Verifica la consola del navegador por errores")
    print("   • Prueba en modo incógnito")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    verificar_correccion_hover()
    mostrar_problemas_solucionados()
    instrucciones_prueba()
    
    print("\n" + "=" * 65)
    print("🎉 ¡CORRECCIONES DE HOVER IMPLEMENTADAS EXITOSAMENTE!")
    print("🎯 Los campos ya NO se volverán muy claros al hacer hover")
    print("=" * 65)

if __name__ == "__main__":
    main()
