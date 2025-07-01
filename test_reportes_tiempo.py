#!/usr/bin/env python
"""
Script de prueba para verificar el sistema de reportes de tiempo de MultiAndamios
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from pedidos.models import Pedido, DetallePedido
from usuarios.models import Usuario, Cliente
from productos.models import Producto

def test_reportes_tiempo():
    """Función principal de prueba"""
    print("🚀 Iniciando prueba del sistema de reportes de tiempo")
    print("=" * 60)
    
    # Verificar que los modelos tienen los métodos necesarios
    print("\n1. Verificando métodos de tiempo en modelos...")
    
    try:
        # Obtener un pedido de prueba
        pedido = Pedido.objects.first()
        if pedido:
            print(f"✅ Pedido encontrado: #{pedido.id_pedido}")
            
            # Probar métodos del pedido
            fecha_inicio = pedido.get_fecha_inicio_renta()
            fecha_fin = pedido.get_fecha_fin_renta()
            tiempo_restante = pedido.get_tiempo_restante_renta()
            estado_tiempo = pedido.get_estado_tiempo_renta()
            tiempo_humanizado = pedido.get_tiempo_restante_renta_humanizado()
            porcentaje = pedido.get_porcentaje_tiempo_transcurrido()
            debe_notificar = pedido.debe_notificar_vencimiento()
            
            print(f"   📅 Fecha inicio: {fecha_inicio}")
            print(f"   📅 Fecha fin: {fecha_fin}")
            print(f"   ⏰ Tiempo restante: {tiempo_restante}")
            print(f"   📊 Estado: {estado_tiempo}")
            print(f"   📝 Humanizado: {tiempo_humanizado}")
            print(f"   📈 Porcentaje: {porcentaje:.1f}%")
            print(f"   🔔 Debe notificar: {debe_notificar}")
            
            # Probar métodos de detalles
            print("\n   Probando detalles del pedido:")
            for detalle in pedido.detalles.all():
                fecha_fin_detalle = detalle.get_fecha_fin_renta_detalle()
                tiempo_restante_detalle = detalle.get_tiempo_restante_renta_detalle()
                estado_tiempo_detalle = detalle.get_estado_tiempo_renta_detalle()
                tiempo_humanizado_detalle = detalle.get_tiempo_restante_humanizado_detalle()
                
                print(f"     🛒 {detalle.producto.nombre}:")
                print(f"       - Fin renta: {fecha_fin_detalle}")
                print(f"       - Tiempo restante: {tiempo_restante_detalle}")
                print(f"       - Estado: {estado_tiempo_detalle}")
                print(f"       - Humanizado: {tiempo_humanizado_detalle}")
            
            print("✅ Todos los métodos funcionan correctamente")
        else:
            print("⚠️ No se encontraron pedidos para probar")
            
    except Exception as e:
        print(f"❌ Error al probar métodos: {e}")
    
    # Verificar URLs
    print("\n2. Verificando configuración de URLs...")
    
    try:
        from django.urls import reverse
        
        urls_to_test = [
            'pedidos:mis_pedidos_tiempo',
            'pedidos:reporte_tiempo_global',
            'pedidos:notificaciones_vencimiento',
            'pedidos:dashboard_tiempo',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name}: {url}")
            except Exception as e:
                print(f"❌ {url_name}: Error - {e}")
                
        # URLs con parámetros
        if pedido:
            try:
                url_detalle = reverse('pedidos:detalle_tiempo_pedido', args=[pedido.id_pedido])
                print(f"✅ detalle_tiempo_pedido: {url_detalle}")
            except Exception as e:
                print(f"❌ detalle_tiempo_pedido: Error - {e}")
        
    except ImportError as e:
        print(f"❌ Error al importar reverse: {e}")
    
    # Verificar templates
    print("\n3. Verificando existencia de templates...")
    
    templates_path = os.path.join(os.path.dirname(__file__), 'pedidos', 'templates', 'pedidos')
    required_templates = [
        'mis_pedidos_tiempo.html',
        'reporte_tiempo_global.html',
        'detalle_tiempo_pedido.html',
        'notificaciones_vencimiento.html',
        'dashboard_tiempo.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join(templates_path, template)
        if os.path.exists(template_path):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - No encontrado")
    
    # Estadísticas de pedidos
    print("\n4. Estadísticas de pedidos...")
    
    try:
        total_pedidos = Pedido.objects.count()
        pedidos_activos = Pedido.objects.filter(
            estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
        ).count()
        
        print(f"📊 Total de pedidos: {total_pedidos}")
        print(f"📊 Pedidos activos: {pedidos_activos}")
        
        if pedidos_activos > 0:
            # Contar por estado de tiempo
            contadores = {
                'vencidos': 0,
                'vence_hoy': 0,
                'vence_pronto': 0,
                'normales': 0,
                'sin_iniciar': 0,
            }
            
            for pedido in Pedido.objects.filter(estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']):
                estado = pedido.get_estado_tiempo_renta()
                if estado == 'vencido':
                    contadores['vencidos'] += 1
                elif estado == 'vence_hoy':
                    contadores['vence_hoy'] += 1
                elif estado == 'vence_pronto':
                    contadores['vence_pronto'] += 1
                elif estado == 'normal':
                    contadores['normales'] += 1
                else:
                    contadores['sin_iniciar'] += 1
            
            print(f"   🚨 Vencidos: {contadores['vencidos']}")
            print(f"   ⏰ Vencen hoy: {contadores['vence_hoy']}")
            print(f"   ⚠️ Vencen pronto: {contadores['vence_pronto']}")
            print(f"   ✅ Normales: {contadores['normales']}")
            print(f"   ⏸️ Sin iniciar: {contadores['sin_iniciar']}")
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Prueba completada")
    print("\n💡 Próximos pasos:")
    print("   1. Ejecutar el servidor: python manage.py runserver")
    print("   2. Acceder como admin a: /panel/admin/tiempo/dashboard/")
    print("   3. Acceder como cliente a: /panel/mis-pedidos/tiempo/")
    print("   4. Verificar que los reportes se muestren correctamente")
    print("   5. Probar las notificaciones en: /panel/admin/tiempo/notificaciones/")

if __name__ == "__main__":
    test_reportes_tiempo()
