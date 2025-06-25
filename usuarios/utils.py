from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

def enviar_correo_pago(pedido, tipo_notificacion):
    """
    Envía correos relacionados con pagos
    tipo_notificacion: 'recordatorio', 'registrado', 'aprobado', 'rechazado', 'vencimiento'
    """
    asuntos = {
        'recordatorio': 'Recordatorio de Pago Pendiente',
        'registrado': 'Pago Registrado - En Revisión',
        'aprobado': 'Pago Aprobado',
        'rechazado': 'Pago Rechazado',
        'vencimiento': '¡Último día para realizar tu pago!'
    }
    
    templates = {
        'recordatorio': 'emails/recordatorio_pago.html',
        'registrado': 'emails/pago_registrado.html',
        'aprobado': 'emails/pago_aprobado.html',
        'rechazado': 'emails/pago_rechazado.html',
        'vencimiento': 'emails/vencimiento_pago.html'
    }
    
    context = {
        'pedido': pedido,
        'cliente': pedido.cliente,
        'tiempo_restante': pedido.get_tiempo_restante_pago(),
        'total': pedido.total
    }
    
    html_content = render_to_string(templates[tipo_notificacion], context)
    
    send_mail(
        subject=asuntos[tipo_notificacion],
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[pedido.cliente.usuario.email],
        html_message=html_content
    )

def verificar_pagos_pendientes():
    """
    Verifica pagos pendientes y envía recordatorios
    """
    from .models import Pedido
    
    # Pedidos pendientes de pago
    pedidos_pendientes = Pedido.objects.filter(
        estado_pedido_general='pendiente_pago'
    )
    
    for pedido in pedidos_pendientes:
        tiempo_restante = pedido.get_tiempo_restante_pago()
        
        if tiempo_restante is None:  # Ya venció
            pedido.estado_pedido_general = 'pago_vencido'
            pedido.save()
            enviar_correo_pago(pedido, 'vencimiento')
            
        elif tiempo_restante.total_seconds() <= 86400:  # Menos de 24 horas
            enviar_correo_pago(pedido, 'recordatorio')
