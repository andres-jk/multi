#!/usr/bin/env python3
"""
Verificación rápida del estado del GPS
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

from pedidos.models import EntregaPedido

# Verificar entregas en camino
entregas_en_camino = EntregaPedido.objects.filter(estado_entrega='en_camino')
print(f"Entregas en camino: {entregas_en_camino.count()}")

for entrega in entregas_en_camino:
    print(f"  - Entrega #{entrega.id} - Pedido #{entrega.pedido.id_pedido}")
    print(f"    GPS: {entrega.latitud_actual}, {entrega.longitud_actual}")
    print(f"    URL: /panel/entregas/cliente/seguimiento/{entrega.pedido.id_pedido}/")
