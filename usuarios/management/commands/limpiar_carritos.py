from django.core.management.base import BaseCommand
from usuarios.models import CarritoItem
from django.utils import timezone

class Command(BaseCommand):
    help = 'Limpia los carritos de compras inactivos por más de 24 horas'

    def handle(self, *args, **kwargs):
        try:
            antes = CarritoItem.objects.filter(reservado=True).count()
            CarritoItem.limpiar_carritos_antiguos()
            despues = CarritoItem.objects.filter(reservado=True).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Se limpiaron {antes - despues} carritos inactivos exitosamente'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error al limpiar carritos: {str(e)}'
                )
            )
