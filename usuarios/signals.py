# Signal temporalmente deshabilitado para evitar conflictos
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Usuario, Cliente

# @receiver(post_save, sender=Usuario)
# def create_cliente_profile(sender, instance, created, **kwargs):
#     """
#     Automatically create a Cliente profile when a new Usuario is created.
#     This ensures that every user has a corresponding Cliente record.
#     Solo se crea si el usuario es de rol 'cliente' y no tiene un cliente asociado.
#     """
#     if created and instance.rol == 'cliente':
#         try:
#             # Verificar si ya existe un cliente para este usuario
#             if not hasattr(instance, 'cliente'):
#                 Cliente.objects.get_or_create(
#                     usuario=instance,
#                     defaults={
#                         'telefono': getattr(instance, 'telefono', ''),
#                         'direccion': getattr(instance, 'direccion', '')
#                     }
#                 )
#         except Exception as e:
#             # Si hay un error, no se crea el cliente automáticamente
#             # Esto evita conflictos con la creación manual
#             pass

# NOTA: Signal deshabilitado temporalmente para solucionar problema de "Este usuario ya tiene un cliente asociado"
# La creación de clientes se maneja manualmente en las vistas correspondientes.
