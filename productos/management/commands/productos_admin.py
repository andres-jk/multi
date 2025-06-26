from django.core.management.base import BaseCommand
from productos.models import Producto

class Command(BaseCommand):
    help = 'Comando para verificar y actualizar productos con el nuevo sistema de renta'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--listar',
            action='store_true',
            help='Lista todos los productos con sus tipos de renta',
        )
        parser.add_argument(
            '--verificar',
            action='store_true',
            help='Verifica que todos los productos tengan tipos de renta válidos',
        )
        parser.add_argument(
            '--calcular-precios',
            action='store_true',
            help='Calcula precios semanales faltantes',
        )
    
    def handle(self, *args, **options):
        if options['listar']:
            self.listar_productos()
        elif options['verificar']:
            self.verificar_productos()
        elif options['calcular_precios']:
            self.calcular_precios_semanales()
        else:
            self.stdout.write(
                self.style.WARNING('Usa --help para ver las opciones disponibles')
            )
    
    def listar_productos(self):
        """Lista todos los productos con sus tipos de renta"""
        self.stdout.write(
            self.style.SUCCESS('📋 Lista de productos:')
        )
        
        productos = Producto.objects.all().order_by('nombre')
        
        for producto in productos:
            estado = "✅ Activo" if producto.activo else "❌ Inactivo"
            precio_semanal = f"${producto.precio_semanal}" if producto.precio_semanal else "No definido"
            
            self.stdout.write(
                f"• {producto.nombre}"
            )
            self.stdout.write(
                f"  Tipo: {producto.get_tipo_renta_display()} | "
                f"Mensual: ${producto.precio} | "
                f"Semanal: {precio_semanal} | "
                f"{estado}"
            )
    
    def verificar_productos(self):
        """Verifica que todos los productos tengan configuraciones válidas"""
        self.stdout.write(
            self.style.SUCCESS('🔍 Verificando productos...')
        )
        
        productos = Producto.objects.all()
        problemas = 0
        
        for producto in productos:
            # Verificar tipo de renta válido
            if producto.tipo_renta not in ['mensual', 'semanal']:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {producto.nombre}: Tipo de renta inválido '{producto.tipo_renta}'"
                    )
                )
                problemas += 1
            
            # Verificar precios
            if producto.precio <= 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {producto.nombre}: Precio mensual debe ser mayor que 0"
                    )
                )
                problemas += 1
            
            # Verificar precio semanal si existe
            if producto.precio_semanal and producto.precio_semanal <= 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {producto.nombre}: Precio semanal debe ser mayor que 0"
                    )
                )
                problemas += 1
        
        if problemas == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos los productos están correctamente configurados')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Se encontraron {problemas} problemas')
            )
    
    def calcular_precios_semanales(self):
        """Calcula y actualiza precios semanales faltantes"""
        self.stdout.write(
            self.style.SUCCESS('💰 Calculando precios semanales faltantes...')
        )
        
        productos_actualizados = 0
        
        for producto in Producto.objects.filter(precio_semanal__isnull=True):
            precio_semanal_calculado = round(producto.precio / 4, 2)
            producto.precio_semanal = precio_semanal_calculado
            producto.save()
            
            self.stdout.write(
                f"✅ {producto.nombre}: Precio semanal calculado = ${precio_semanal_calculado}"
            )
            productos_actualizados += 1
        
        if productos_actualizados == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos los productos ya tienen precio semanal definido')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Se actualizaron {productos_actualizados} productos'
                )
            )
