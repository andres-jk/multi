from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, Cliente


@receiver(post_save, sender=Usuario)
def create_cliente_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Cliente profile when a new Usuario is created.
    This ensures that every user has a corresponding Cliente record.
    """
    if created:
        Cliente.objects.get_or_create(
            usuario=instance,
            defaults={
                'telefono': getattr(instance, 'telefono', ''),
                'direccion': getattr(instance, 'direccion', '')
            }
        )
