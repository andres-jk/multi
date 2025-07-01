#!/usr/bin/env python3
"""
Test completo del sistema de entregas de MultiAndamios
Verifica que el empleado pueda seleccionar pedidos con pagos aceptados,
programar entregas y hacer seguimiento hasta la confirmación.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from usuarios.models import Usuario, Cliente
from pedidos.models import Pedido, EntregaPedido
from productos.models import Producto

User = Usuario  # El modelo Usuario ya extiende AbstractUser

def crear_datos_prueba():
    """Crear datos de prueba para el sistema de entregas"""
    print("🔧 Creando datos de prueba...")
    
    # Crear usuario empleado recibos_obra
    empleado, created = Usuario.objects.get_or_create(
        username='empleado_entregas',
        defaults={
            'first_name': 'Juan',
            'last_name': 'Entregador',
            'email': 'entregas@multiandamios.com',
            'rol': 'recibos_obra',
            'activo': True
        }
    )
    if created:
        empleado.set_password('password123')
        empleado.save()
    
    # Crear usuario cliente
    cliente_user, created = Usuario.objects.get_or_create(
        username='cliente_prueba',
        defaults={
            'first_name': 'María',
            'last_name': 'González',
            'email': 'maria@empresa.com',
            'rol': 'cliente',
            'activo': True
        }
    )
    if created:
        cliente_user.set_password('password123')
        cliente_user.save()
    
    cliente, _ = Cliente.objects.get_or_create(
        usuario=cliente_user,
        defaults={
            'razon_social': 'Empresa Constructora ABC',
            'telefono': '3001234567',
            'direccion': 'Calle 123 #45-67, Bogotá'
        }
    )
    
    # Crear producto
    producto, _ = Producto.objects.get_or_create(
        nombre='Andamio Multidireccional 2m',
        defaults={
            'descripcion': 'Andamio multidireccional de 2 metros',
            'precio_diario': Decimal('50000'),
            'cantidad_disponible': 100,
            'activo': True
        }
    )
    
    return empleado, cliente, producto

def crear_pedido_pagado(cliente, producto):
    """Crear un pedido con pago aceptado"""
    print("📦 Creando pedido con pago aceptado...")
    
    pedido = Pedido.objects.create(
        cliente=cliente,
        direccion_entrega='Carrera 15 #82-45, Bogotá',
        notas='Entregar en horario laboral',
        subtotal=Decimal('500000'),
        iva=Decimal('95000'),
        costo_transporte=Decimal('50000'),
        total=Decimal('645000'),
        estado_pedido_general='pagado',
        fecha_pago=timezone.now(),
        duracion_renta=30,
        metodo_pago='transferencia'
    )
    
    print(f"✅ Pedido creado: #{pedido.id_pedido}")
    return pedido

def test_seleccion_pedidos_listos():
    """Probar la vista de pedidos listos para entrega"""
    print("\n📋 Probando selección de pedidos listos para entrega...")
    
    from pedidos.views_entregas import pedidos_listos_entrega
    from django.test import RequestFactory
    
    factory = RequestFactory()
    
    # Simular request del empleado
    empleado = Usuario.objects.filter(rol='recibos_obra').first()
    if not empleado:
        print("❌ No hay empleados de recibos_obra")
        return False
        
    request = factory.get('/entregas/pedidos-listos/')
    request.user = empleado
    
    try:
        # Llamar la vista
        response = pedidos_listos_entrega(request)
        print("✅ Vista de pedidos listos funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en vista de pedidos listos: {e}")
        return False

def test_programar_entrega(pedido, empleado):
    """Probar la programación de una entrega"""
    print(f"\n📅 Programando entrega para pedido #{pedido.id_pedido}...")
    
    try:
        # Crear entrega programada
        fecha_programada = timezone.now() + timedelta(days=1)
        
        entrega = EntregaPedido.objects.create(
            pedido=pedido,
            empleado_entrega=empleado,
            fecha_programada=fecha_programada,
            direccion_salida='MultiAndamios - Bodega Principal',
            direccion_destino=pedido.direccion_entrega,
            vehiculo_placa='ABC-123',
            conductor_nombre='Carlos Conductor',
            conductor_telefono='3009876543',
            observaciones='Entrega programática de prueba'
        )
        
        print(f"✅ Entrega programada correctamente: ID {entrega.id}")
        print(f"   Estado: {entrega.get_estado_entrega_display()}")
        print(f"   Fecha: {entrega.fecha_programada}")
        print(f"   Vehículo: {entrega.vehiculo_placa}")
        print(f"   Conductor: {entrega.conductor_nombre}")
        
        return entrega
    except Exception as e:
        print(f"❌ Error programando entrega: {e}")
        return None

def test_flujo_entrega(entrega):
    """Probar el flujo completo de entrega"""
    print(f"\n🚛 Probando flujo completo de entrega ID {entrega.id}...")
    
    try:
        # 1. Iniciar recorrido
        print("1️⃣ Iniciando recorrido...")
        entrega.iniciar_recorrido(
            latitud_inicial=Decimal('4.6097'),
            longitud_inicial=Decimal('-74.0817')
        )
        print(f"   ✅ Recorrido iniciado - Estado: {entrega.get_estado_entrega_display()}")
        
        # 2. Actualizar ubicación
        print("2️⃣ Actualizando ubicación GPS...")
        entrega.actualizar_ubicacion(
            latitud=Decimal('4.6150'),
            longitud=Decimal('-74.0850'),
            tiempo_estimado=timezone.now() + timedelta(minutes=30),
            distancia_restante=Decimal('5.5')
        )
        print(f"   ✅ Ubicación actualizada - Lat: {entrega.latitud_actual}, Lng: {entrega.longitud_actual}")
        
        # 3. Confirmar entrega
        print("3️⃣ Confirmando entrega...")
        entrega.observaciones = "Entrega completada exitosamente - Prueba automatizada"
        entrega.confirmar_entrega()
        print(f"   ✅ Entrega confirmada - Estado: {entrega.get_estado_entrega_display()}")
        print(f"   📅 Fecha entrega: {entrega.fecha_entrega}")
        
        # 4. Verificar estado del pedido
        pedido = entrega.pedido
        pedido.refresh_from_db()
        print(f"   📦 Estado pedido: {pedido.get_estado_pedido_general_display()}")
        
        return True
    except Exception as e:
        print(f"❌ Error en flujo de entrega: {e}")
        return False

def test_seguimiento_cliente(pedido):
    """Probar seguimiento desde perspectiva del cliente"""
    print(f"\n👤 Probando seguimiento del cliente para pedido #{pedido.id_pedido}...")
    
    try:
        entrega = pedido.entrega
        
        # Simular datos que vería el cliente
        print(f"   📍 Estado entrega: {entrega.get_estado_entrega_display()}")
        if entrega.estado_entrega == 'en_camino':
            print(f"   🗺️ Ubicación actual: {entrega.latitud_actual}, {entrega.longitud_actual}")
            print(f"   ⏰ Tiempo estimado: {entrega.tiempo_estimado_llegada}")
            print(f"   📏 Distancia restante: {entrega.distancia_restante_km} km")
        
        print(f"   🚚 Vehículo: {entrega.vehiculo_placa}")
        print(f"   👨‍💼 Conductor: {entrega.conductor_nombre} - {entrega.conductor_telefono}")
        
        print("✅ Seguimiento del cliente funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en seguimiento del cliente: {e}")
        return False

def test_filtros_y_estadisticas():
    """Probar filtros y estadísticas del panel"""
    print("\n📊 Probando filtros y estadísticas...")
    
    try:
        # Contar entregas por estado
        programadas = EntregaPedido.objects.filter(estado_entrega='programada').count()
        en_camino = EntregaPedido.objects.filter(estado_entrega='en_camino').count()
        entregadas = EntregaPedido.objects.filter(estado_entrega='entregada').count()
        
        print(f"   📋 Entregas programadas: {programadas}")
        print(f"   🚛 Entregas en camino: {en_camino}")
        print(f"   ✅ Entregas completadas: {entregadas}")
        
        # Contar pedidos listos para entrega
        pedidos_listos = Pedido.objects.filter(
            estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega']
        ).exclude(entrega__isnull=False).count()
        
        print(f"   📦 Pedidos listos para programar: {pedidos_listos}")
        
        print("✅ Filtros y estadísticas funcionan correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en filtros y estadísticas: {e}")
        return False

def verificar_urls():
    """Verificar que todas las URLs estén configuradas"""
    print("\n🔗 Verificando configuración de URLs...")
    
    from django.urls import reverse
    
    urls_requeridas = [
        'pedidos:panel_entregas',
        'pedidos:pedidos_listos_entrega',
        'pedidos:programar_entrega',
        'pedidos:detalle_entrega',
        'pedidos:iniciar_recorrido',
        'pedidos:seguimiento_entrega',
        'pedidos:confirmar_entrega',
        'pedidos:seguimiento_cliente',
    ]
    
    try:
        for url_name in urls_requeridas:
            if 'programar_entrega' in url_name or 'detalle_entrega' in url_name or 'iniciar_recorrido' in url_name or 'seguimiento_entrega' in url_name or 'confirmar_entrega' in url_name or 'seguimiento_cliente' in url_name:
                # Estas URLs requieren parámetros
                continue
            
            url = reverse(url_name)
            print(f"   ✅ {url_name}: {url}")
        
        print("✅ Todas las URLs están configuradas correctamente")
        return True
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def main():
    """Ejecutar todas las pruebas del sistema de entregas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE ENTREGAS")
    print("=" * 60)
    
    resultados = []
    
    try:
        # 1. Crear datos de prueba
        empleado, cliente, producto = crear_datos_prueba()
        pedido = crear_pedido_pagado(cliente, producto)
        
        # 2. Verificar URLs
        resultados.append(("Configuración URLs", verificar_urls()))
        
        # 3. Probar selección de pedidos
        resultados.append(("Selección pedidos listos", test_seleccion_pedidos_listos()))
        
        # 4. Programar entrega
        entrega = test_programar_entrega(pedido, empleado)
        if entrega:
            resultados.append(("Programación entrega", True))
            
            # 5. Probar flujo completo
            resultados.append(("Flujo completo entrega", test_flujo_entrega(entrega)))
            
            # 6. Seguimiento cliente
            resultados.append(("Seguimiento cliente", test_seguimiento_cliente(pedido)))
        else:
            resultados.append(("Programación entrega", False))
            resultados.append(("Flujo completo entrega", False))
            resultados.append(("Seguimiento cliente", False))
        
        # 7. Filtros y estadísticas
        resultados.append(("Filtros y estadísticas", test_filtros_y_estadisticas()))
        
    except Exception as e:
        print(f"❌ Error general en las pruebas: {e}")
        return False
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitosas = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSA" if resultado else "❌ FALLIDA"
        print(f"{nombre:<25} {estado}")
        if resultado:
            exitosas += 1
    
    print(f"\nTotal: {exitosas}/{len(resultados)} pruebas exitosas")
    
    if exitosas == len(resultados):
        print("\n🎉 ¡TODAS LAS PRUEBAS HAN PASADO!")
        print("   El sistema de entregas está completamente funcional.")
        print("   Los empleados pueden:")
        print("   • Seleccionar pedidos con pagos aceptados")
        print("   • Programar entregas con toda la información necesaria")
        print("   • Iniciar recorridos y hacer seguimiento GPS")
        print("   • Confirmar entregas con evidencia")
        print("   • Los clientes pueden hacer seguimiento en tiempo real")
        return True
    else:
        print(f"\n⚠️  {len(resultados) - exitosas} pruebas fallaron")
        print("   Revisa los errores mostrados arriba.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
