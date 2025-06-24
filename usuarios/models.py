from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('recibos_obra', 'Empleado de Recibos de Obra'),
        ('cliente', 'Cliente'),
    )
    numero_identidad = models.CharField(max_length=20, unique=True, verbose_name='Número de Identidad', null=True, blank=True)  # Permite nulos temporalmente
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    direccion = models.CharField(max_length=255, blank=True, null=True)
    
    def puede_ver_recibos(self):
        """Determina si el usuario puede acceder a la sección de recibos de obra"""
        return self.rol in ['admin', 'recibos_obra'] or self.is_staff

    def __str__(self):
        return self.username

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente', null=True, blank=True)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.usuario:
            return f"{self.usuario.first_name} {self.usuario.last_name}"
        return "Cliente sin usuario asignado"

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')
    calle = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.departamento}"

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

class MetodoPago(models.Model):
    TIPO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('cheque', 'Cheque'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('debito', 'Tarjeta Débito'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    numero_referencia = models.CharField(max_length=100, blank=True, null=True)
    comprobante = models.FileField(upload_to='comprobantes_pago/', blank=True, null=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default='pendiente')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_pago}"

class CarritoItem(models.Model):
    """Modelo para los items en el carrito de compras"""
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='items_carrito',
        verbose_name='Usuario'
    )
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    meses_renta = models.PositiveIntegerField(
        default=1,
        verbose_name='Meses de renta'
    )
    fecha_agregado = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de agregado'
    )
    reservado = models.BooleanField(
        default=False,
        verbose_name='Reservado'
    )

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        # Asegurar que no haya duplicados para el mismo usuario y producto
        unique_together = ['usuario', 'producto']

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad}) - {self.usuario.username}"

    def subtotal(self):
        return self.producto.precio * self.cantidad * self.meses_renta

    def liberar_reserva(self):
        """Libera la reserva del producto y lo devuelve al inventario"""
        if self.reservado:
            self.producto.cantidad_disponible += self.cantidad
            self.producto.cantidad_reservada -= self.cantidad
            self.producto.save()
            self.reservado = False
            self.save()

    @classmethod
    def limpiar_carritos_antiguos(cls):
        """Limpia los carritos que tienen más de 24 horas sin actividad"""
        limite_tiempo = timezone.now() - timedelta(hours=24)
        carritos_antiguos = cls.objects.filter(fecha_agregado__lt=limite_tiempo, reservado=True)
        
        for item in carritos_antiguos:
            item.liberar_reserva()
        
        carritos_antiguos.delete()
