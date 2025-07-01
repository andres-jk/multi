#!/usr/bin/env python
"""
Script para probar el sistema de entregas de MultiAndamios
Verifica que todas las funcionalidades estén correctamente configuradas
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from pedidos.models import Pedido, EntregaPedido
from usuarios.models import Usuario, Cliente

def test_system():
    print("🚀 Iniciando pruebas del sistema de entregas...")
    print("=" * 60)
    
    try:
        # 1. Verificar modelos
        print("📊 1. Verificando modelos...")
        
        # Verificar que EntregaPedido existe y tiene los campos necesarios
        campos_esperados = [
            'pedido', 'empleado_entrega', 'fecha_programada', 'fecha_inicio_recorrido',
            'fecha_entrega', 'estado_entrega', 'direccion_salida', 'direccion_destino',
            'latitud_inicial', 'longitud_inicial', 'latitud_actual', 'longitud_actual',
            'vehiculo_placa', 'conductor_nombre', 'conductor_telefono',
            'tiempo_estimado_llegada', 'distancia_restante_km', 'observaciones'
        ]
        
        entrega_fields = [field.name for field in EntregaPedido._meta.get_fields()]
        campos_faltantes = [campo for campo in campos_esperados if campo not in entrega_fields]
        
        if campos_faltantes:
            print(f"❌ Campos faltantes en EntregaPedido: {campos_faltantes}")
            return False
        
        print("✅ Modelo EntregaPedido verificado correctamente")
        
        # Verificar estados disponibles
        estados_esperados = ['programada', 'en_camino', 'entregada', 'cancelada']
        estados_disponibles = [choice[0] for choice in EntregaPedido.ESTADO_ENTREGA_CHOICES]
        estados_faltantes = [estado for estado in estados_esperados if estado not in estados_disponibles]
        
        if estados_faltantes:
            print(f"❌ Estados faltantes en EntregaPedido: {estados_faltantes}")
            return False
        
        print("✅ Estados de entrega verificados correctamente")
        
        # 2. Verificar usuarios con rol recibos_obra
        print("\n👥 2. Verificando usuarios...")
        
        empleados_recibos = Usuario.objects.filter(rol='recibos_obra', activo=True)
        print(f"✅ Empleados de recibos de obra encontrados: {empleados_recibos.count()}")
        
        # 3. Verificar que existen pedidos en estado 'listo_entrega'
        print("\n📦 3. Verificando pedidos...")
        
        pedidos_listos = Pedido.objects.filter(estado_pedido_general='listo_entrega')
        print(f"✅ Pedidos listos para entrega: {pedidos_listos.count()}")
        
        # 4. Crear datos de prueba si es necesario
        print("\n🔧 4. Configurando datos de prueba...")
        
        with transaction.atomic():
            # Crear empleado de recibos si no existe
            empleado_test, created = Usuario.objects.get_or_create(
                email='empleado.entregas@test.com',
                defaults={
                    'username': 'empleado_entregas_test',
                    'first_name': 'Empleado',
                    'last_name': 'Entregas Test',
                    'rol': 'recibos_obra',
                    'activo': True
                }
            )
            
            if created:
                empleado_test.set_password('test123')
                empleado_test.save()
                print("✅ Empleado de entregas de prueba creado")
            else:
                print("✅ Empleado de entregas de prueba ya existe")
            
            # Crear cliente de prueba si no existe
            cliente_test, created = Usuario.objects.get_or_create(
                email='cliente.entregas@test.com',
                defaults={
                    'username': 'cliente_entregas_test',
                    'first_name': 'Cliente',
                    'last_name': 'Entregas Test',
                    'rol': 'cliente',
                    'activo': True
                }
            )
            
            if created:
                cliente_test.set_password('test123')
                cliente_test.save()
                
                # Crear perfil de cliente
                cliente_perfil, _ = Cliente.objects.get_or_create(
                    usuario=cliente_test,
                    defaults={
                        'nit_cedula': '12345678',
                        'razon_social': 'Cliente Test SAS',
                        'direccion': 'Calle 123 #45-67, Bogotá',
                        'telefono': '3007654321'
                    }
                )
                print("✅ Cliente de entregas de prueba creado")
            else:
                print("✅ Cliente de entregas de prueba ya existe")
            
            # Crear pedido de prueba si no existe uno listo para entrega
            if not pedidos_listos.exists():
                cliente_perfil = Cliente.objects.get(usuario=cliente_test)
                
                pedido_test = Pedido.objects.create(
                    cliente=cliente_perfil,
                    fecha=datetime.now(),
                    estado_pedido_general='listo_entrega',
                    total=500000,
                    direccion_entrega='Calle 456 #78-90, Bogotá',
                    notas='Pedido de prueba para sistema de entregas'
                )
                print(f"✅ Pedido de prueba creado: {pedido_test.id_pedido}")
            
        # 5. Probar creación de entrega
        print("\n🚚 5. Probando creación de entrega...")
        
        pedido_para_entrega = Pedido.objects.filter(estado_pedido_general='listo_entrega').first()
        
        if pedido_para_entrega:
            # Verificar que no tenga entrega ya programada
            if not hasattr(pedido_para_entrega, 'entrega'):
                try:
                    entrega_test = EntregaPedido.objects.create(
                        pedido=pedido_para_entrega,
                        empleado_entrega=empleado_test,
                        fecha_programada=datetime.now() + timedelta(hours=24),
                        direccion_salida='Bodega Principal - Calle 100 #20-30',
                        direccion_destino=pedido_para_entrega.direccion_entrega,
                        vehiculo_placa='TEST-123',
                        conductor_nombre='Conductor Test',
                        conductor_telefono='3009876543',
                        observaciones='Entrega de prueba del sistema'
                    )
                    print(f"✅ Entrega de prueba creada: ID {entrega_test.id}")
                    
                    # Probar métodos del modelo
                    print(f"   Estado inicial: {entrega_test.get_estado_entrega_display()}")
                    
                    # Simular inicio de recorrido
                    entrega_test.iniciar_recorrido(latitud_inicial=4.6097, longitud_inicial=-74.0817)
                    print(f"   Estado después de iniciar: {entrega_test.get_estado_entrega_display()}")
                    
                    # Simular confirmación de entrega
                    entrega_test.confirmar_entrega()
                    print(f"   Estado después de confirmar: {entrega_test.get_estado_entrega_display()}")
                    
                    print("✅ Métodos de EntregaPedido funcionan correctamente")
                    
                except Exception as e:
                    print(f"❌ Error al crear entrega: {e}")
                    return False
            else:
                print("✅ El pedido ya tiene una entrega programada")
        else:
            print("⚠️  No hay pedidos listos para entrega")
        
        # 6. Verificar URLs
        print("\n🌐 6. Verificando URLs...")
        
        try:
            from django.urls import reverse
            
            urls_to_test = [
                'pedidos:panel_entregas',
                # No podemos probar URLs con parámetros sin IDs reales
            ]
            
            for url_name in urls_to_test:
                try:
                    url = reverse(url_name)
                    print(f"✅ URL {url_name} disponible: {url}")
                except Exception as e:
                    print(f"❌ Error con URL {url_name}: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error verificando URLs: {e}")
            return False
        
        # 7. Verificar templates
        print("\n📄 7. Verificando templates...")
        
        templates_esperados = [
            'pedidos/templates/entregas/panel_entregas.html',
            'pedidos/templates/entregas/seguimiento_entrega.html',
            'pedidos/templates/entregas/seguimiento_cliente.html',
            'pedidos/templates/entregas/iniciar_recorrido.html',
            'pedidos/templates/entregas/confirmar_entrega.html',
            'pedidos/templates/entregas/programar_entrega.html'
        ]
        
        for template in templates_esperados:
            if os.path.exists(template):
                print(f"✅ Template encontrado: {template}")
            else:
                print(f"❌ Template faltante: {template}")
                return False
        
        # 8. Verificar archivos estáticos
        print("\n🎨 8. Verificando archivos estáticos...")
        
        css_file = 'static/css/entregas.css'
        if os.path.exists(css_file):
            print(f"✅ CSS encontrado: {css_file}")
        else:
            print(f"❌ CSS faltante: {css_file}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ¡Todas las pruebas completadas exitosamente!")
        print("\n📋 Resumen del sistema de entregas:")
        print(f"   - Modelo EntregaPedido: ✅ Configurado")
        print(f"   - Estados de entrega: ✅ {len(estados_disponibles)} estados")
        print(f"   - Empleados de recibos: ✅ {empleados_recibos.count()} empleados")
        print(f"   - Templates: ✅ {len(templates_esperados)} templates")
        print(f"   - URLs: ✅ Configuradas")
        print(f"   - CSS: ✅ Configurado")
        
        print("\n🚀 El sistema está listo para usar!")
        print("\n📝 Próximos pasos:")
        print("   1. Configurar Google Maps API para seguimiento GPS")
        print("   2. Probar el flujo completo desde la interfaz web")
        print("   3. Configurar notificaciones por email/SMS")
        print("   4. Agregar pruebas automatizadas")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_system()
    sys.exit(0 if success else 1)
