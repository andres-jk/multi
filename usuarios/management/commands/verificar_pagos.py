from django.core.management.base import BaseCommand
from django.utils import timezone
from usuarios.utils import verificar_pagos_pendientes

class Command(BaseCommand):
    help = 'Verifica pagos pendientes y envía recordatorios'

    def handle(self, *args, **options):
        try:
            verificar_pagos_pendientes()
            self.stdout.write(self.style.SUCCESS('Verificación de pagos completada exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al verificar pagos: {str(e)}'))
