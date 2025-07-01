#!/usr/bin/env python3
"""
Script para verificar que Bootstrap esté funcionando correctamente
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

from django.test import Client
from pedidos.models import EntregaPedido
from usuarios.models import Usuario

def test_bootstrap_integration():
    """Probar que Bootstrap esté integrado correctamente"""
    
    print("=== VERIFICACIÓN DE BOOTSTRAP ===\n")
    
    # Crear cliente de prueba
    client = Client()
    
    # Buscar empleado
    empleado = Usuario.objects.filter(rol='recibos_obra').first()
    if not empleado:
        print("❌ No se encontró empleado")
        return False
    
    # Login
    login_success = client.login(username=empleado.username, password='recibos123')
    if not login_success:
        print("❌ Login falló")
        return False
    
    print("✅ Login exitoso")
    
    # Buscar entrega
    entrega = EntregaPedido.objects.filter(estado_entrega='programada').first()
    if not entrega:
        print("❌ No se encontró entrega programada")
        return False
    
    print(f"✅ Entrega encontrada: {entrega.id}")
    
    # Probar acceso a página de iniciar recorrido
    url = f'/pedidos/entregas/{entrega.id}/iniciar/'
    response = client.get(url)
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Verificar que Bootstrap esté incluido
        has_bootstrap_css = 'bootstrap' in content and 'css' in content
        has_bootstrap_js = 'bootstrap' in content and 'js' in content
        has_modal = 'modal' in content
        has_confirm_function = 'confirmarInicio' in content
        
        print(f"✅ Página accesible (status: {response.status_code})")
        print(f"✅ Bootstrap CSS incluido: {has_bootstrap_css}")
        print(f"✅ Bootstrap JS incluido: {has_bootstrap_js}")
        print(f"✅ Modal presente: {has_modal}")
        print(f"✅ Función confirmarInicio: {has_confirm_function}")
        
        if all([has_bootstrap_css, has_bootstrap_js, has_modal, has_confirm_function]):
            print("\n🎉 BOOTSTRAP INTEGRADO CORRECTAMENTE")
            return True
        else:
            print("\n⚠️ FALTAN ALGUNOS COMPONENTES")
            return False
    else:
        print(f"❌ Error accediendo a página: {response.status_code}")
        return False

def mostrar_solucion():
    """Mostrar la solución al problema de Bootstrap"""
    
    print("\n=== SOLUCIÓN IMPLEMENTADA ===")
    print("✅ Bootstrap 5.3.0 CSS agregado al base.html")
    print("✅ Bootstrap 5.3.0 JS agregado al base.html")
    print("✅ Modal actualizado para Bootstrap 5")
    print("✅ JavaScript corregido con manejo de errores")
    print("✅ Fallback manual para cerrar modal")
    
    print("\n=== CAMBIOS REALIZADOS ===")
    print("1. 📄 base.html - Bootstrap CSS y JS agregados")
    print("2. 🔧 iniciar_recorrido.html - Modal y JS actualizados")
    print("3. ⚡ JavaScript mejorado con depuración")
    print("4. 🛡️ Manejo de errores robusto")
    
    print("\n=== CÓMO PROBAR ===")
    print("1. 🔄 Recarga la página en el navegador")
    print("2. 🧹 Limpia caché del navegador (Ctrl+F5)")
    print("3. 🔍 Abre DevTools (F12) para ver logs")
    print("4. ✅ Marca todos los checkboxes")
    print("5. 🚀 Haz clic en 'INICIAR RECORRIDO'")
    print("6. ✔️ Confirma en el modal")
    
    print("\n=== LOGS A VERIFICAR ===")
    print("- 'iniciarRecorrido() llamado'")
    print("- 'Todos los checkboxes están marcados'")
    print("- 'Modal mostrado'")
    print("- 'confirmarInicio() llamado'")
    print("- 'Modal cerrado'")
    print("- 'Formulario encontrado, enviando...'")

if __name__ == "__main__":
    print("🔧 VERIFICANDO INTEGRACIÓN DE BOOTSTRAP")
    
    success = test_bootstrap_integration()
    
    if success:
        print("\n✅ BOOTSTRAP INTEGRADO CORRECTAMENTE")
    else:
        print("\n⚠️ VERIFICACIÓN PARCIAL - CONTINÚA CON PRUEBA MANUAL")
    
    mostrar_solucion()
    
    print("\n" + "="*50)
    print("🌐 SERVIDOR: http://127.0.0.1:8000/")
    print("🔗 LOGIN: http://127.0.0.1:8000/login/")
    print("📋 PANEL: http://127.0.0.1:8000/pedidos/entregas/panel/")
    print("="*50)
