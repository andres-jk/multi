from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from pedidos.models import Pedido
from datetime import timedelta

class Command(BaseCommand):
    help = 'Envía recordatorios de vencimiento y recogida de pedidos'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # Recordatorios de vencimiento (7 días antes)
        pedidos_por_vencer = Pedido.objects.filter(
            fecha_vencimiento__range=(now, now + timedelta(days=7)),
            estado_pedido_general='totalmente_entregado',
            recordatorio_enviado=False
        )
        
        for pedido in pedidos_por_vencer:
            try:
                subject = f'Recordatorio de vencimiento - Pedido #{pedido.id_pedido}'
                message = f"""
                Estimado {pedido.cliente},
                
                Le recordamos que su pedido #{pedido.id_pedido} vence el {pedido.fecha_vencimiento.strftime('%d/%m/%Y')}.
                Por favor programe la devolución de los productos antes de esta fecha para evitar cargos adicionales.
                
                Saludos,
                MultiAndamios
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [pedido.cliente.usuario.email],
                    fail_silently=False,
                )
                
                pedido.recordatorio_enviado = True
                pedido.ultimo_recordatorio = now
                pedido.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Recordatorio enviado para pedido #{pedido.id_pedido}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error enviando recordatorio para pedido #{pedido.id_pedido}: {str(e)}'
                    )
                )
