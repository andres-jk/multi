from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Verifica la integridad del sistema y reporta errores'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando verificación del sistema...'))
        
        # Verificar modelos
        self.verify_models()
        
        # Verificar migraciones
        self.verify_migrations()
        
        # Verificar URLs
        self.verify_urls()
        
        self.stdout.write(self.style.SUCCESS('✅ Verificación del sistema completada'))

    def verify_models(self):
        """Verifica que todos los modelos estén correctamente definidos"""
        self.stdout.write('🔍 Verificando modelos...')
        
        try:
            # Verificar modelo Pedido
            Pedido = apps.get_model('pedidos', 'Pedido')
            DetallePedido = apps.get_model('pedidos', 'DetallePedido')
            
            # Verificar que los campos existen
            pedido_fields = [f.name for f in Pedido._meta.fields]
            detalle_fields = [f.name for f in DetallePedido._meta.fields]
            
            required_pedido_fields = ['ref_pago', 'estado_pedido_general']
            required_detalle_fields = ['estado']
            
            for field in required_pedido_fields:
                if field not in pedido_fields:
                    self.stdout.write(self.style.ERROR(f'❌ Campo faltante en Pedido: {field}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'✅ Campo Pedido.{field} existe'))
            
            for field in required_detalle_fields:
                if field not in detalle_fields:
                    self.stdout.write(self.style.ERROR(f'❌ Campo faltante en DetallePedido: {field}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'✅ Campo DetallePedido.{field} existe'))
            
            # Verificar modelos de recibos
            ReciboObra = apps.get_model('recibos', 'ReciboObra')
            DetalleReciboObra = apps.get_model('recibos', 'DetalleReciboObra')
            
            self.stdout.write(self.style.SUCCESS('✅ Todos los modelos están disponibles'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error verificando modelos: {str(e)}'))

    def verify_migrations(self):
        """Verifica el estado de las migraciones"""
        self.stdout.write('🔍 Verificando migraciones...')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT app, name FROM django_migrations WHERE app IN ('pedidos', 'recibos', 'usuarios', 'productos')")
                migrations = cursor.fetchall()
                
                apps_with_migrations = set(migration[0] for migration in migrations)
                expected_apps = {'pedidos', 'recibos', 'usuarios', 'productos'}
                
                for app in expected_apps:
                    if app in apps_with_migrations:
                        self.stdout.write(self.style.SUCCESS(f'✅ App {app} tiene migraciones'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠️  App {app} no tiene migraciones aplicadas'))
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error verificando migraciones: {str(e)}'))

    def verify_urls(self):
        """Verifica que las URLs estén configuradas correctamente"""
        self.stdout.write('🔍 Verificando configuración de URLs...')
        
        try:
            from django.urls import reverse
            
            # URLs críticas a verificar
            critical_urls = [
                'usuarios:inicio_cliente',
                'usuarios:carrito',
                'pedidos:lista_pedidos',
                'recibos:lista_recibos',
                'productos:catalogo_productos',
            ]
            
            for url_name in critical_urls:
                try:
                    reverse(url_name)
                    self.stdout.write(self.style.SUCCESS(f'✅ URL {url_name} configurada correctamente'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error en URL {url_name}: {str(e)}'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error verificando URLs: {str(e)}'))
