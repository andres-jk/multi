"""
Comando para crear un usuario administrador de prueba
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea un usuario administrador de prueba para gestión de empleados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nombre de usuario del administrador (por defecto: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña del administrador (por defecto: admin123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@multiandamios.com',
            help='Email del administrador'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        # Verificar si ya existe un administrador
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario "{username}" ya existe.')
            )
            return
        
        # Crear el usuario administrador
        try:
            admin_user = Usuario.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name='Administrador',
                last_name='Sistema',
                rol='admin',
                is_staff=True,
                is_superuser=True,
                numero_identidad='00000000',
                activo=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Usuario administrador "{username}" creado exitosamente.\n'
                    f'Credenciales:\n'
                    f'  Usuario: {username}\n'
                    f'  Contraseña: {password}\n'
                    f'  Email: {email}\n'
                    f'  Rol: Administrador\n'
                    f'\nPuede usar estas credenciales para acceder al sistema '
                    f'y gestionar empleados.'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear el administrador: {str(e)}')
            )
