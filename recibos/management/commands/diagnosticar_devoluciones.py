"""
Comando para diagnosticar y corregir problemas de devolución de productos
"""
from django.core.management.base import BaseCommand
from django.db.models import F
from productos.models import Producto
from recibos.models import ReciboObra, DetalleReciboObra
from django.db import transaction


class Command(BaseCommand):
    help = 'Diagnostica y corrige problemas de devolución de productos en recibos de obra'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corregir automáticamente las inconsistencias encontradas',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DIAGNÓSTICO DE DEVOLUCIÓN DE PRODUCTOS ==='))
        
        fix_mode = options['fix']
        verbose = options['verbose']
        
        # 1. Verificar estado general de productos
        self.verificar_productos(verbose)
        
        # 2. Verificar recibos pendientes
        problemas_simples = self.verificar_recibos_simples(verbose)
        
        # 3. Verificar recibos consolidados
        problemas_consolidados = self.verificar_recibos_consolidados(verbose)
        
        # 4. Mostrar resumen
        total_problemas = len(problemas_simples) + len(problemas_consolidados)
        
        if total_problemas > 0:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️ Se encontraron {total_problemas} problemas de devolución')
            )
            
            if fix_mode:
                self.corregir_problemas(problemas_simples, problemas_consolidados)
            else:
                self.stdout.write(
                    self.style.NOTICE('💡 Ejecuta con --fix para corregir automáticamente')
                )
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ No se encontraron problemas de devolución'))

    def verificar_productos(self, verbose):
        """Verificar el estado general de los productos"""
        self.stdout.write('\n📦 ESTADO DE PRODUCTOS:')
        
        productos = Producto.objects.all()
        productos_con_renta = productos.filter(cantidad_en_renta__gt=0)
        
        self.stdout.write(f'   Total productos: {productos.count()}')
        self.stdout.write(f'   Productos con stock en renta: {productos_con_renta.count()}')
        
        if verbose and productos_con_renta.exists():
            for producto in productos_con_renta[:5]:
                self.stdout.write(
                    f'     • {producto.nombre}: '
                    f'Disponible={producto.cantidad_disponible}, '
                    f'En renta={producto.cantidad_en_renta}, '
                    f'Reservada={producto.cantidad_reservada}'
                )

    def verificar_recibos_simples(self, verbose):
        """Verificar recibos simples con productos pendientes"""
        self.stdout.write('\n📄 RECIBOS SIMPLES PENDIENTES:')
        
        recibos_pendientes = ReciboObra.objects.filter(
            cantidad_vuelta__lt=F('cantidad_solicitada')
        )
        
        problemas = []
        
        self.stdout.write(f'   Recibos con productos pendientes: {recibos_pendientes.count()}')
        
        for recibo in recibos_pendientes:
            pendiente = recibo.cantidad_solicitada - recibo.cantidad_vuelta
            
            if verbose or pendiente > 0:
                self.stdout.write(
                    f'     • Recibo #{recibo.id}: {pendiente} de {recibo.cantidad_solicitada} '
                    f'unidades de {recibo.producto.nombre} pendientes'
                )
            
            # Verificar si hay inconsistencia con el inventario
            if recibo.producto.cantidad_en_renta < pendiente:
                problemas.append({
                    'tipo': 'simple',
                    'recibo': recibo,
                    'pendiente': pendiente,
                    'en_renta': recibo.producto.cantidad_en_renta,
                    'problema': 'inconsistencia_inventario'
                })
                
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f'       ⚠️ PROBLEMA: Solo hay {recibo.producto.cantidad_en_renta} '
                            f'en renta pero se necesitan {pendiente} para completar la devolución'
                        )
                    )
        
        return problemas

    def verificar_recibos_consolidados(self, verbose):
        """Verificar detalles de recibos consolidados con productos pendientes"""
        self.stdout.write('\n📋 RECIBOS CONSOLIDADOS PENDIENTES:')
        
        detalles_pendientes = DetalleReciboObra.objects.filter(
            cantidad_vuelta__lt=F('cantidad_solicitada')
        )
        
        problemas = []
        
        self.stdout.write(f'   Detalles con productos pendientes: {detalles_pendientes.count()}')
        
        for detalle in detalles_pendientes:
            pendiente = detalle.cantidad_solicitada - detalle.cantidad_vuelta
            
            if verbose or pendiente > 0:
                self.stdout.write(
                    f'     • Detalle #{detalle.id} (Recibo #{detalle.recibo.id}): '
                    f'{pendiente} de {detalle.cantidad_solicitada} '
                    f'unidades de {detalle.producto.nombre} pendientes'
                )
            
            # Verificar inconsistencia con el inventario
            if detalle.producto.cantidad_en_renta < pendiente:
                problemas.append({
                    'tipo': 'consolidado',
                    'detalle': detalle,
                    'pendiente': pendiente,
                    'en_renta': detalle.producto.cantidad_en_renta,
                    'problema': 'inconsistencia_inventario'
                })
                
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(
                            f'       ⚠️ PROBLEMA: Solo hay {detalle.producto.cantidad_en_renta} '
                            f'en renta pero se necesitan {pendiente} para completar la devolución'
                        )
                    )
        
        return problemas

    def corregir_problemas(self, problemas_simples, problemas_consolidados):
        """Corregir los problemas encontrados"""
        self.stdout.write('\n🔧 CORRIGIENDO PROBLEMAS...')
        
        corregidos = 0
        
        with transaction.atomic():
            # Corregir problemas en recibos simples
            for problema in problemas_simples:
                if self.corregir_recibo_simple(problema):
                    corregidos += 1
            
            # Corregir problemas en recibos consolidados
            for problema in problemas_consolidados:
                if self.corregir_recibo_consolidado(problema):
                    corregidos += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Se corrigieron {corregidos} problemas')
        )

    def corregir_recibo_simple(self, problema):
        """Corregir un problema en un recibo simple"""
        recibo = problema['recibo']
        pendiente = problema['pendiente']
        
        try:
            # Mover productos disponibles a en renta si es necesario
            producto = recibo.producto
            faltante = pendiente - producto.cantidad_en_renta
            
            if faltante > 0 and producto.cantidad_disponible >= faltante:
                producto.cantidad_disponible -= faltante
                producto.cantidad_en_renta += faltante
                producto.save()
                
                self.stdout.write(
                    f'   ✅ Recibo #{recibo.id}: Movidos {faltante} productos '
                    f'de disponible a en renta para {producto.nombre}'
                )
                return True
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'   ❌ Recibo #{recibo.id}: No hay suficientes productos '
                        f'disponibles para corregir la inconsistencia'
                    )
                )
                return False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Error corrigiendo recibo #{recibo.id}: {e}')
            )
            return False

    def corregir_recibo_consolidado(self, problema):
        """Corregir un problema en un detalle de recibo consolidado"""
        detalle = problema['detalle']
        pendiente = problema['pendiente']
        
        try:
            # Mover productos disponibles a en renta si es necesario
            producto = detalle.producto
            faltante = pendiente - producto.cantidad_en_renta
            
            if faltante > 0 and producto.cantidad_disponible >= faltante:
                producto.cantidad_disponible -= faltante
                producto.cantidad_en_renta += faltante
                producto.save()
                
                self.stdout.write(
                    f'   ✅ Detalle #{detalle.id}: Movidos {faltante} productos '
                    f'de disponible a en renta para {producto.nombre}'
                )
                return True
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'   ❌ Detalle #{detalle.id}: No hay suficientes productos '
                        f'disponibles para corregir la inconsistencia'
                    )
                )
                return False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Error corrigiendo detalle #{detalle.id}: {e}')
            )
            return False
