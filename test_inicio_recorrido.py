#!/usr/bin/env python3
"""
Script para probar completamente el sistema de inicio de recorridos
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
from django.contrib.auth import authenticate
from pedidos.models import Pedido, EntregaPedido
from usuarios.models import Usuario

def test_inicio_recorrido():
    """Probar el inicio de recorrido con cliente de prueba"""
    
    print("=== PRUEBA DE INICIO DE RECORRIDO ===\n")
    
    # Crear cliente de prueba
    client = Client()
    
    # Buscar empleado de entregas
    empleado = Usuario.objects.filter(rol='recibos_obra').first()
    if not empleado:
        print("❌ No se encontró empleado de entregas")
        return False
        
    print(f"✅ Empleado encontrado: {empleado.username}")
    
    # Intentar login
    login_success = client.login(username=empleado.username, password='recibos123')
    if not login_success:
        print("❌ No se pudo hacer login")
        return False
        
    print("✅ Login exitoso")
    
    # Buscar entrega programada
    entrega = EntregaPedido.objects.filter(
        estado_entrega='programada',
        empleado_entrega=empleado
    ).first()
    
    if not entrega:
        print("❌ No se encontró entrega programada para este empleado")
        return False
        
    print(f"✅ Entrega encontrada: ID {entrega.id}")
    
    # Probar acceso a la página de iniciar recorrido
    url_iniciar = f'/pedidos/entregas/{entrega.id}/iniciar/'
    response = client.get(url_iniciar)
    
    if response.status_code != 200:
        print(f"❌ Error accediendo a página de inicio: {response.status_code}")
        return False
        
    print("✅ Página de inicio de recorrido accesible")
    
    # Probar POST para iniciar recorrido
    post_data = {
        'latitud': '4.6097',
        'longitud': '-74.0817',
    }
    
    response = client.post(url_iniciar, post_data)
    
    # Verificar redirección exitosa
    if response.status_code in [200, 302]:
        print("✅ POST exitoso para iniciar recorrido")
        
        # Recargar entrega desde BD
        entrega.refresh_from_db()
        
        if entrega.estado_entrega == 'en_camino':
            print("✅ Estado cambiado correctamente a 'en_camino'")
            print(f"✅ Fecha inicio: {entrega.fecha_inicio_recorrido}")
            print(f"✅ Ubicación inicial: {entrega.latitud_inicial}, {entrega.longitud_inicial}")
            return True
        else:
            print(f"❌ Estado no cambió correctamente: {entrega.estado_entrega}")
            return False
    else:
        print(f"❌ Error en POST: {response.status_code}")
        print(f"Contenido: {response.content.decode()[:200]}...")
        return False

def mostrar_instrucciones():
    """Mostrar instrucciones detalladas para el usuario"""
    
    print("\n=== INSTRUCCIONES PARA PROBAR MANUALMENTE ===")
    print("\n1. 🌐 Ve a: http://127.0.0.1:8000/login/")
    print("   Credenciales: carlos_recibos / recibos123")
    print("   (o cualquier empleado con rol 'recibos_obra')")
    
    print("\n2. 📋 Panel de Entregas:")
    print("   - Verás una lista de entregas programadas")
    print("   - Busca una con estado 'Programada'")
    print("   - Haz clic en 'Ver Detalles' o 'Iniciar Recorrido'")
    
    print("\n3. ✅ Lista de Verificación:")
    print("   - Marca todos los checkboxes del checklist")
    print("   - Verifica que el GPS obtenga ubicación (opcional)")
    print("   - El botón 'INICIAR RECORRIDO' debe habilitarse")
    
    print("\n4. 🚀 Iniciar Recorrido:")
    print("   - Haz clic en 'INICIAR RECORRIDO'")
    print("   - Aparecerá un modal de confirmación")
    print("   - Haz clic en 'Sí, Iniciar Recorrido'")
    print("   - Deberías ser redirigido a la página de seguimiento")
    
    print("\n5. 📍 Verificar Estado:")
    print("   - La entrega debería cambiar a estado 'En Camino'")
    print("   - Deberías ver la página de seguimiento GPS")
    print("   - El cliente podrá ver el seguimiento en tiempo real")
    
    print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
    print("   - Si el botón no se habilita: Verifica que todos los checkboxes estén marcados")
    print("   - Si el modal no aparece: Verifica la consola del navegador (F12)")
    print("   - Si hay error al enviar: Verifica los logs del servidor Django")
    print("   - Si GPS no funciona: Permite permisos de ubicación en el navegador")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE ENTREGAS")
    
    # Ejecutar prueba automatizada
    success = test_inicio_recorrido()
    
    if success:
        print("\n🎉 PRUEBA AUTOMATIZADA EXITOSA")
        print("✅ El sistema de inicio de recorridos funciona correctamente")
    else:
        print("\n⚠️ PRUEBA AUTOMATIZADA FALLÓ")
        print("ℹ️ Esto podría ser normal - prueba manualmente")
    
    # Mostrar instrucciones
    mostrar_instrucciones()
    
    print("\n" + "="*60)
    print("🔗 SERVIDOR CORRIENDO EN: http://127.0.0.1:8000/")
    print("📱 ACCESO DIRECTO AL PANEL: http://127.0.0.1:8000/pedidos/entregas/panel/")
    print("="*60)
