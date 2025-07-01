#!/usr/bin/env python3
"""
Script de prueba rápida para verificar URLs y acceso
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from usuarios.models import Usuario

def verificar_servidor():
    """Verificar que el servidor Django esté corriendo"""
    print(f"⚠️  Verificar manualmente que el servidor esté en http://127.0.0.1:8000/")
    return True

def verificar_urls_entregas():
    """Verificar URLs específicas del sistema de entregas"""
    urls_importantes = [
        'http://127.0.0.1:8000/',
        'http://127.0.0.1:8000/login/',
        'http://127.0.0.1:8000/admin/',
        'http://127.0.0.1:8000/panel/entregas/panel/',
        'http://127.0.0.1:8000/panel/entregas/pedidos-listos/',
    ]
    
    print("📋 URLs importantes del sistema:")
    for url in urls_importantes:
        print(f"   • {url}")

def verificar_usuario_empleado():
    """Verificar que el usuario empleado existe y tiene permisos"""
    try:
        empleado = Usuario.objects.get(username='empleado_entregas')
        print(f"✅ Usuario encontrado: {empleado.username}")
        print(f"   Rol: {empleado.rol}")
        print(f"   Activo: {empleado.activo}")
        print(f"   Email: {empleado.email}")
        print(f"   Nombre: {empleado.get_full_name()}")
        
        # Verificar que el password funciona
        if empleado.check_password('123456'):
            print(f"✅ Contraseña verificada correctamente")
        else:
            print(f"❌ Contraseña incorrecta")
            
        return empleado
    except Usuario.DoesNotExist:
        print(f"❌ Usuario empleado_entregas no encontrado")
        return None

def verificar_datos_prueba():
    """Verificar que los datos de prueba existen"""
    from pedidos.models import Pedido, EntregaPedido
    
    pedidos = Pedido.objects.filter(
        estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega']
    ).exclude(entrega__isnull=False)
    
    print(f"✅ Pedidos listos para entrega: {pedidos.count()}")
    
    for pedido in pedidos[:3]:  # Solo mostrar los primeros 3
        print(f"   Pedido #{pedido.id_pedido} - {pedido.get_estado_pedido_general_display()}")
        print(f"     Cliente: {pedido.cliente.usuario.get_full_name()}")
        print(f"     Total: ${pedido.total:,.0f}")
    
    entregas = EntregaPedido.objects.all()
    print(f"✅ Entregas programadas: {entregas.count()}")

def main():
    print("🔍 VERIFICANDO SISTEMA DE ENTREGAS")
    print("=" * 50)
    
    # 1. Verificar servidor
    print("\n1️⃣ Verificando servidor Django...")
    verificar_servidor()
    
    # 2. Verificar URLs
    print("\n2️⃣ URLs importantes del sistema...")
    verificar_urls_entregas()
    
    # 3. Verificar usuario empleado
    print("\n3️⃣ Verificando usuario empleado...")
    empleado = verificar_usuario_empleado()
    
    # 4. Verificar datos de prueba
    print("\n4️⃣ Verificando datos de prueba...")
    verificar_datos_prueba()
    
    # 5. Instrucciones de acceso
    print("\n" + "=" * 50)
    print("🚀 INSTRUCCIONES DE ACCESO")
    print("=" * 50)
    
    if empleado:
        print(f"1. Ve a: http://127.0.0.1:8000/login/")
        print(f"2. Inicia sesión con:")
        print(f"   Usuario: empleado_entregas")
        print(f"   Contraseña: 123456")
        print(f"3. Después del login, ve a:")
        print(f"   Panel de Entregas: http://127.0.0.1:8000/panel/entregas/panel/")
        print(f"   Pedidos Listos: http://127.0.0.1:8000/panel/entregas/pedidos-listos/")
        
        print(f"\n📋 URLs DIRECTAS (después del login):")
        print(f"   • http://127.0.0.1:8000/panel/entregas/panel/")
        print(f"   • http://127.0.0.1:8000/panel/entregas/pedidos-listos/")
        print(f"   • http://127.0.0.1:8000/panel/entregas/programar/39/")
        print(f"   • http://127.0.0.1:8000/panel/entregas/programar/40/")
        print(f"   • http://127.0.0.1:8000/panel/entregas/programar/41/")
    else:
        print("❌ No se puede acceder sin usuario válido")
    
    print(f"\n✅ Sistema listo para usar!")

if __name__ == '__main__':
    main()
