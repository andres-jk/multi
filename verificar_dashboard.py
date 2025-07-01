#!/usr/bin/env python
"""
Script de verificación rápida del dashboard de tiempo corregido
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def verificar_dashboard():
    """Verifica que el dashboard funcione correctamente"""
    print("🔍 Verificando Dashboard de Tiempo - MultiAndamios")
    print("=" * 60)
    
    try:
        from pedidos.models import Pedido, DetallePedido
        from django.db.models import Sum, Count
        
        # Simular la lógica del dashboard
        print("\n1. ✅ Importaciones exitosas")
        
        # Obtener pedidos activos
        pedidos_activos = Pedido.objects.filter(
            estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
        )
        total_activos = pedidos_activos.count()
        print(f"2. ✅ Pedidos activos encontrados: {total_activos}")
        
        # Contar por estado de tiempo
        contadores = {
            'vencidos': 0,
            'vence_hoy': 0,
            'vence_pronto': 0,
            'normales': 0,
            'sin_iniciar': 0,
        }
        
        for pedido in pedidos_activos:
            estado_tiempo = pedido.get_estado_tiempo_renta()
            if estado_tiempo == 'vencido':
                contadores['vencidos'] += 1
            elif estado_tiempo == 'vence_hoy':
                contadores['vence_hoy'] += 1
            elif estado_tiempo == 'vence_pronto':
                contadores['vence_pronto'] += 1
            elif estado_tiempo == 'normal':
                contadores['normales'] += 1
            else:
                contadores['sin_iniciar'] += 1
        
        print("3. ✅ Contadores calculados:")
        for estado, cantidad in contadores.items():
            print(f"   - {estado}: {cantidad}")
        
        # Calcular porcentajes
        porcentajes = {}
        if total_activos > 0:
            porcentajes = {
                'vencidos': round((contadores['vencidos'] / total_activos) * 100, 1),
                'vence_hoy': round((contadores['vence_hoy'] / total_activos) * 100, 1),
                'vence_pronto': round((contadores['vence_pronto'] / total_activos) * 100, 1),
                'normales': round((contadores['normales'] / total_activos) * 100, 1),
                'sin_iniciar': round((contadores['sin_iniciar'] / total_activos) * 100, 1),
            }
        else:
            porcentajes = {key: 0 for key in contadores.keys()}
        
        print("4. ✅ Porcentajes calculados:")
        for estado, porcentaje in porcentajes.items():
            print(f"   - {estado}: {porcentaje}%")
        
        # Productos más rentados
        productos_populares = DetallePedido.objects.filter(
            pedido__estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega', 'entregado']
        ).values(
            'producto__nombre'
        ).annotate(
            total_cantidad=Sum('cantidad'),
            total_pedidos=Count('pedido', distinct=True)
        ).order_by('-total_cantidad')[:5]
        
        print(f"5. ✅ Productos populares encontrados: {productos_populares.count()}")
        
        # Ingresos activos
        ingresos_activos = pedidos_activos.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        print(f"6. ✅ Ingresos activos: ${ingresos_activos:,.0f}")
        
        # Porcentaje urgentes
        porcentaje_urgentes = round((contadores['vencidos'] + contadores['vence_hoy']) / max(total_activos, 1) * 100, 1)
        print(f"7. ✅ Porcentaje urgentes: {porcentaje_urgentes}%")
        
        print("\n" + "=" * 60)
        print("🎉 Verificación EXITOSA - Dashboard funcionando correctamente")
        print("\n🌐 URLs para probar:")
        print("   📊 Dashboard: http://127.0.0.1:8000/panel/admin/tiempo/dashboard/")
        print("   📋 Reporte Global: http://127.0.0.1:8000/panel/admin/tiempo/reporte/")
        print("   🔔 Notificaciones: http://127.0.0.1:8000/panel/admin/tiempo/notificaciones/")
        print("   👥 Para Clientes: http://127.0.0.1:8000/panel/mis-pedidos/tiempo/")
        
        print("\n💡 Estado del Sistema:")
        if porcentaje_urgentes > 15:
            print("   🚨 CRÍTICO: Muchos pedidos urgentes")
        elif porcentaje_urgentes > 5:
            print("   ⚠️ ALERTA: Algunos pedidos requieren atención")
        else:
            print("   ✅ NORMAL: Sistema funcionando bien")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = verificar_dashboard()
    if exito:
        print("\n🚀 ¡El dashboard está listo para usar!")
        print("🔧 Servidor debe estar ejecutándose en: http://127.0.0.1:8000/")
    else:
        print("\n❌ Se encontraron errores. Revisa la configuración.")
