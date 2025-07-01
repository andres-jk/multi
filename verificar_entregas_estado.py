#!/usr/bin/env python3
"""
Script para verificar y arreglar el estado de las entregas para permitir iniciar recorridos
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

from pedidos.models import Pedido, EntregaPedido
from usuarios.models import Usuario

def verificar_y_arreglar_entregas():
    """Verificar el estado de las entregas y arreglar si es necesario"""
    
    print("=== VERIFICACIÓN DE ENTREGAS ===\n")
    
    # Verificar entregas existentes
    entregas = EntregaPedido.objects.all()
    print(f"Total de entregas encontradas: {entregas.count()}")
    
    for entrega in entregas:
        print(f"\nEntrega ID: {entrega.id}")
        print(f"Pedido: {entrega.pedido.id_pedido}")
        print(f"Estado actual: {entrega.estado_entrega} ({entrega.get_estado_entrega_display()})")
        print(f"Empleado: {entrega.empleado_entrega.username if entrega.empleado_entrega else 'No asignado'}")
        print(f"Fecha programada: {entrega.fecha_programada}")
        
        # Si la entrega no está en estado 'programada', cambiarla
        if entrega.estado_entrega != 'programada':
            print(f"❌ Cambiando estado de '{entrega.estado_entrega}' a 'programada'")
            entrega.estado_entrega = 'programada'
            entrega.fecha_inicio_recorrido = None
            entrega.fecha_entrega = None
            entrega.latitud_inicial = None
            entrega.longitud_inicial = None
            entrega.latitud_actual = None
            entrega.longitud_actual = None
            entrega.save()
            print("✅ Estado actualizado")
        else:
            print("✅ Estado correcto")
    
    print("\n=== CREANDO ENTREGA DE PRUEBA SI ES NECESARIO ===\n")
    
    # Verificar si hay al menos una entrega en estado 'programada'
    entregas_programadas = EntregaPedido.objects.filter(estado_entrega='programada')
    
    if not entregas_programadas.exists():
        print("No hay entregas programadas. Creando una de prueba...")
        
        # Buscar un pedido elegible
        pedido_elegible = Pedido.objects.filter(
            estado_pedido_general__in=['pagado', 'en_preparacion', 'listo_entrega']
        ).exclude(
            entrega__isnull=False
        ).first()
        
        if pedido_elegible:
            # Buscar empleado de entregas
            empleado = Usuario.objects.filter(rol='recibos_obra').first()
            
            if empleado:
                entrega_prueba = EntregaPedido.objects.create(
                    pedido=pedido_elegible,
                    empleado_entrega=empleado,
                    fecha_programada='2024-12-20 10:00:00',
                    direccion_salida='Bodega MultiAndamios, Calle 123 #45-67',
                    direccion_destino=pedido_elegible.direccion_entrega or 'Dirección de entrega',
                    vehiculo_placa='ABC123',
                    conductor_nombre='Juan Pérez',
                    conductor_telefono='3001234567',
                    observaciones='Entrega de prueba para testing'
                )
                
                print(f"✅ Entrega de prueba creada: ID {entrega_prueba.id}")
                print(f"   Pedido: {pedido_elegible.id_pedido}")
                print(f"   Empleado: {empleado.username}")
            else:
                print("❌ No se encontró empleado de entregas")
        else:
            print("❌ No se encontró pedido elegible para crear entrega")
    else:
        print(f"✅ Se encontraron {entregas_programadas.count()} entregas programadas")
    
    print("\n=== RESUMEN FINAL ===")
    entregas_por_estado = {}
    for estado, display in EntregaPedido.ESTADO_ENTREGA_CHOICES:
        count = EntregaPedido.objects.filter(estado_entrega=estado).count()
        if count > 0:
            entregas_por_estado[display] = count
    
    for estado, count in entregas_por_estado.items():
        print(f"- {estado}: {count}")
    
    print(f"\n✅ Total entregas programadas (listas para iniciar): {EntregaPedido.objects.filter(estado_entrega='programada').count()}")
    
    return True

if __name__ == "__main__":
    success = verificar_y_arreglar_entregas()
    if success:
        print("\n🎉 VERIFICACIÓN COMPLETADA")
        print("\nPara probar:")
        print("1. Ve a: http://127.0.0.1:8000/login/")
        print("2. Credenciales: carlos_recibos / recibos123")
        print("3. Ve a Panel de Entregas")
        print("4. Selecciona una entrega programada")
        print("5. Haz clic en 'Iniciar Recorrido'")
    else:
        print("\n❌ VERIFICACIÓN FALLÓ")
        sys.exit(1)
