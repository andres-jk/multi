"""
Comando para crear empleados de prueba con diferentes permisos
"""
from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea empleados de prueba con diferentes permisos para testing'

    def handle(self, *args, **options):
        empleados_prueba = [
            {
                'username': 'juan_productos',
                'password': 'emp123',
                'email': 'juan@multiandamios.com',
                'first_name': 'Juan',
                'last_name': 'García',
                'numero_identidad': '12345678',
                'rol': 'empleado',
                'permisos': {
                    'puede_gestionar_productos': True,
                    'puede_gestionar_inventario': True,
                }
            },
            {
                'username': 'maria_pedidos',
                'password': 'emp123',
                'email': 'maria@multiandamios.com',
                'first_name': 'María',
                'last_name': 'López',
                'numero_identidad': '87654321',
                'rol': 'empleado',
                'permisos': {
                    'puede_gestionar_pedidos': True,
                    'puede_gestionar_clientes': True,
                }
            },
            {
                'username': 'carlos_recibos',
                'password': 'emp123',
                'email': 'carlos@multiandamios.com',
                'first_name': 'Carlos',
                'last_name': 'Martínez',
                'numero_identidad': '11223344',
                'rol': 'recibos_obra',
                'permisos': {
                    'puede_gestionar_recibos': True,
                    'puede_ver_reportes': True,
                }
            },
            {
                'username': 'ana_pagos',
                'password': 'emp123',
                'email': 'ana@multiandamios.com',
                'first_name': 'Ana',
                'last_name': 'González',
                'numero_identidad': '44332211',
                'rol': 'empleado',
                'permisos': {
                    'puede_procesar_pagos': True,
                    'puede_ver_reportes': True,
                    'puede_gestionar_clientes': True,
                }
            },
            {
                'username': 'pedro_completo',
                'password': 'emp123',
                'email': 'pedro@multiandamios.com',
                'first_name': 'Pedro',
                'last_name': 'Ramírez',
                'numero_identidad': '55667788',
                'rol': 'empleado',
                'permisos': {
                    'puede_gestionar_productos': True,
                    'puede_gestionar_pedidos': True,
                    'puede_gestionar_recibos': True,
                    'puede_gestionar_clientes': True,
                    'puede_ver_reportes': True,
                    'puede_gestionar_inventario': True,
                    'puede_procesar_pagos': True,
                }
            }
        ]

        creados = 0
        existentes = 0

        for empleado_data in empleados_prueba:
            username = empleado_data['username']
            
            if Usuario.objects.filter(username=username).exists():
                existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'El empleado "{username}" ya existe.')
                )
                continue

            try:
                permisos = empleado_data.pop('permisos')
                empleado = Usuario.objects.create_user(**empleado_data)
                
                # Asignar permisos específicos
                for permiso, valor in permisos.items():
                    setattr(empleado, permiso, valor)
                
                empleado.activo = True
                empleado.save()
                
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Empleado "{username}" creado exitosamente.')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error al crear empleado "{username}": {str(e)}')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'Resumen:\n'
                f'  Empleados creados: {creados}\n'
                f'  Empleados existentes: {existentes}\n'
                f'  Total empleados de prueba: {len(empleados_prueba)}\n\n'
                f'Credenciales de acceso:\n'
                f'  Contraseña para todos: emp123\n'
                f'  Usuarios: juan_productos, maria_pedidos, carlos_recibos, ana_pagos, pedro_completo\n\n'
                f'Cada empleado tiene diferentes permisos para probar el sistema.'
            )
        )
