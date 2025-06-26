from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Aplica migraciones y verifica la tabla EstadoProductoIndividual'

    def handle(self, *args, **options):
        self.stdout.write("Aplicando migraciones...")
        
        try:
            # Aplicar migraciones
            call_command('migrate', 'recibos', verbosity=2)
            self.stdout.write(self.style.SUCCESS("Migraciones aplicadas exitosamente"))
            
            # Verificar que la tabla existe
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='recibos_estadoproductoindividual';
                """)
                result = cursor.fetchone()
                
                if result:
                    self.stdout.write(self.style.SUCCESS("Tabla recibos_estadoproductoindividual existe"))
                else:
                    self.stdout.write(self.style.ERROR("Tabla recibos_estadoproductoindividual NO existe"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
