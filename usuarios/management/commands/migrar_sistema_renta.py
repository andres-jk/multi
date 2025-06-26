from django.core.management.base import BaseCommand
from usuarios.models import CarritoItem
from productos.models import Producto

class Command(BaseCommand):
    help = 'Migra los datos existentes del carrito al nuevo sistema de renta'

    def handle(self, *args, **options):
        # Actualizar CarritoItems existentes
        items_actualizados = 0
        for item in CarritoItem.objects.all():
            if not item.periodo_renta:
                item.periodo_renta = item.meses_renta
                item.tipo_renta = 'mensual'  # Por defecto mensual
                item.save()
                items_actualizados += 1
        
        # Actualizar Productos para calcular precio semanal
        productos_actualizados = 0
        for producto in Producto.objects.all():
            if not producto.precio_semanal and producto.precio:
                producto.precio_semanal = round(producto.precio / 4, 2)
                producto.save()
                productos_actualizados += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Migración completada:\n'
                f'- {items_actualizados} items de carrito actualizados\n'
                f'- {productos_actualizados} productos actualizados con precios semanales'
            )
        )
