from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import os

from pedidos.models import Pedido, EntregaPedido
from usuarios.models import Usuario, Cliente


class Command(BaseCommand):
    help = 'Configura y gestiona el sistema de entregas de MultiAndamios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Configura el sistema de entregas inicial'
        )
        
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Crea datos de prueba para el sistema de entregas'
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='Muestra el estado actual del sistema de entregas'
        )
        
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Limpia datos de prueba'
        )

    def handle(self, *args, **options):
        if options['setup']:
            self.setup_delivery_system()
        elif options['create_test_data']:
            self.create_test_data()
        elif options['status']:
            self.show_status()
        elif options['cleanup']:
            self.cleanup_test_data()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Especifica una opción: --setup, --create-test-data, --status, o --cleanup'
                )
            )

    def setup_delivery_system(self):
        """Configuración inicial del sistema de entregas"""
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Configurando sistema de entregas...')
        )
        
        try:
            # Verificar que las migraciones estén aplicadas
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos_entregapedido';"
                )
                if not cursor.fetchone():
                    self.stdout.write(
                        self.style.ERROR(
                            '❌ Tabla pedidos_entregapedido no encontrada. '
                            'Ejecuta: python manage.py migrate'
                        )
                    )
                    return
            
            # Verificar que existen usuarios con rol recibos_obra
            empleados_recibos = Usuario.objects.filter(rol='recibos_obra', activo=True)
            if not empleados_recibos.exists():
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  No hay empleados con rol "recibos_obra". '
                        'Crea usuarios con este rol para usar el sistema.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Encontrados {empleados_recibos.count()} empleados de recibos de obra'
                    )
                )
            
            # Verificar templates
            templates_required = [
                'pedidos/templates/entregas/panel_entregas.html',
                'pedidos/templates/entregas/seguimiento_entrega.html',
                'pedidos/templates/entregas/seguimiento_cliente.html',
                'pedidos/templates/entregas/iniciar_recorrido.html',
                'pedidos/templates/entregas/confirmar_entrega.html',
                'pedidos/templates/entregas/programar_entrega.html'
            ]
            
            missing_templates = []
            for template in templates_required:
                if not os.path.exists(template):
                    missing_templates.append(template)
            
            if missing_templates:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Templates faltantes: {", ".join(missing_templates)}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '✅ Todos los templates están disponibles'
                    )
                )
            
            # Verificar CSS
            css_file = 'static/css/entregas.css'
            if os.path.exists(css_file):
                self.stdout.write(
                    self.style.SUCCESS('✅ Archivo CSS de entregas encontrado')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Archivo CSS faltante: {css_file}')
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\n🎉 Sistema de entregas configurado correctamente!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la configuración: {e}')
            )

    def create_test_data(self):
        """Crea datos de prueba para el sistema"""
        self.stdout.write(
            self.style.HTTP_INFO('🔧 Creando datos de prueba...')
        )
        
        try:
            with transaction.atomic():
                # Crear empleado de entregas
                empleado, created = Usuario.objects.get_or_create(
                    email='empleado.entregas@multiandamios.com',
                    defaults={
                        'username': 'empleado_entregas',
                        'first_name': 'Juan Carlos',
                        'last_name': 'Rodríguez',
                        'rol': 'recibos_obra',
                        'activo': True,
                        'telefono': '3151234567'
                    }
                )
                
                if created:
                    empleado.set_password('entregas2024')
                    empleado.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Empleado de entregas creado: {empleado.email}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Empleado ya existe: {empleado.email}'
                        )
                    )
                
                # Crear cliente de prueba
                cliente_usuario, created = Usuario.objects.get_or_create(
                    email='cliente.test@multiandamios.com',
                    defaults={
                        'username': 'cliente_test',
                        'first_name': 'María',
                        'last_name': 'González',
                        'rol': 'cliente',
                        'activo': True,
                        'telefono': '3207654321'
                    }
                )
                
                if created:
                    cliente_usuario.set_password('cliente2024')
                    cliente_usuario.save()
                    
                    # Crear perfil de cliente
                    cliente_perfil = Cliente.objects.create(
                        usuario=cliente_usuario,
                        nit_cedula='1234567890',
                        razon_social='Constructora González SAS',
                        direccion='Carrera 15 #85-23, Bogotá',
                        telefono='3207654321'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Cliente de prueba creado: {cliente_usuario.email}'
                        )
                    )
                else:
                    cliente_perfil = Cliente.objects.get(usuario=cliente_usuario)
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Cliente ya existe: {cliente_usuario.email}'
                        )
                    )
                
                # Crear pedidos de prueba
                pedidos_estados = [
                    ('listo_entrega', 'Pedido listo para programar entrega'),
                    ('listo_entrega', 'Pedido urgente para entrega mañana'),
                ]
                
                for estado, observacion in pedidos_estados:
                    pedido = Pedido.objects.create(
                        cliente=cliente_perfil,
                        fecha_pedido=timezone.now() - timedelta(days=1),
                        estado_pedido_general=estado,
                        valor_total=750000,
                        direccion_entrega='Obra Constructora González - Calle 127 #45-67, Bogotá',
                        observaciones=observacion
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Pedido creado: #{pedido.id_pedido} - {estado}'
                        )
                    )
                
                # Crear una entrega programada de ejemplo
                pedido_para_entrega = Pedido.objects.filter(
                    estado_pedido_general='listo_entrega'
                ).first()
                
                if pedido_para_entrega and not hasattr(pedido_para_entrega, 'entrega'):
                    entrega = EntregaPedido.objects.create(
                        pedido=pedido_para_entrega,
                        empleado_entrega=empleado,
                        fecha_programada=timezone.now() + timedelta(hours=8),
                        direccion_salida='Bodega Principal MultiAndamios - Calle 80 #30-15',
                        direccion_destino=pedido_para_entrega.direccion_entrega,
                        vehiculo_placa='MAN-456',
                        conductor_nombre='Carlos Pérez',
                        conductor_telefono='3189876543',
                        observaciones='Entrega programada - datos de prueba'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Entrega programada creada: ID {entrega.id}'
                        )
                    )
                
            self.stdout.write(
                self.style.SUCCESS(
                    '\n🎉 Datos de prueba creados correctamente!'
                )
            )
            self.stdout.write('📝 Credenciales de prueba:')
            self.stdout.write('   Empleado: empleado.entregas@multiandamios.com / entregas2024')
            self.stdout.write('   Cliente: cliente.test@multiandamios.com / cliente2024')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando datos de prueba: {e}')
            )

    def show_status(self):
        """Muestra el estado actual del sistema"""
        self.stdout.write(
            self.style.HTTP_INFO('📊 Estado del Sistema de Entregas')
        )
        self.stdout.write('=' * 50)
        
        # Estadísticas generales
        total_entregas = EntregaPedido.objects.count()
        empleados_recibos = Usuario.objects.filter(rol='recibos_obra', activo=True).count()
        pedidos_listos = Pedido.objects.filter(estado_pedido_general='listo_entrega').count()
        
        self.stdout.write(f'📦 Total de entregas registradas: {total_entregas}')
        self.stdout.write(f'👥 Empleados de recibos activos: {empleados_recibos}')
        self.stdout.write(f'🚚 Pedidos listos para entrega: {pedidos_listos}')
        
        # Estadísticas por estado
        if total_entregas > 0:
            self.stdout.write('\n📈 Entregas por estado:')
            for estado_code, estado_name in EntregaPedido.ESTADO_ENTREGA_CHOICES:
                count = EntregaPedido.objects.filter(estado_entrega=estado_code).count()
                if count > 0:
                    self.stdout.write(f'   {estado_name}: {count}')
        
        # Entregas activas (en camino)
        entregas_activas = EntregaPedido.objects.filter(estado_entrega='en_camino')
        if entregas_activas.exists():
            self.stdout.write('\n🚛 Entregas en camino:')
            for entrega in entregas_activas:
                tiempo_en_ruta = entrega.tiempo_en_ruta if hasattr(entrega, 'tiempo_en_ruta') else 'N/A'
                self.stdout.write(
                    f'   Pedido #{entrega.pedido.id_pedido} - '
                    f'{entrega.conductor_nombre} ({entrega.vehiculo_placa}) - '
                    f'Tiempo en ruta: {tiempo_en_ruta} min'
                )
        
        # Entregas programadas para hoy
        hoy = timezone.now().date()
        entregas_hoy = EntregaPedido.objects.filter(
            fecha_programada__date=hoy,
            estado_entrega='programada'
        )
        
        if entregas_hoy.exists():
            self.stdout.write(f'\n📅 Entregas programadas para hoy: {entregas_hoy.count()}')
            for entrega in entregas_hoy:
                self.stdout.write(
                    f'   {entrega.fecha_programada.strftime("%H:%M")} - '
                    f'Pedido #{entrega.pedido.id_pedido} - '
                    f'{entrega.empleado_entrega.get_full_name()}'
                )

    def cleanup_test_data(self):
        """Limpia los datos de prueba"""
        self.stdout.write(
            self.style.WARNING('🧹 Limpiando datos de prueba...')
        )
        
        try:
            with transaction.atomic():
                # Eliminar entregas de prueba
                entregas_test = EntregaPedido.objects.filter(
                    observaciones__icontains='datos de prueba'
                )
                count_entregas = entregas_test.count()
                entregas_test.delete()
                
                # Eliminar pedidos de prueba
                pedidos_test = Pedido.objects.filter(
                    observaciones__icontains='prueba'
                )
                count_pedidos = pedidos_test.count()
                pedidos_test.delete()
                
                # Eliminar usuarios de prueba
                usuarios_test = Usuario.objects.filter(
                    email__in=[
                        'empleado.entregas@multiandamios.com',
                        'cliente.test@multiandamios.com'
                    ]
                )
                count_usuarios = usuarios_test.count()
                usuarios_test.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Limpieza completada:\n'
                        f'   - {count_entregas} entregas eliminadas\n'
                        f'   - {count_pedidos} pedidos eliminados\n'
                        f'   - {count_usuarios} usuarios eliminados'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la limpieza: {e}')
            )
