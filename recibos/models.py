from django.db import models
from django.utils import timezone
from pedidos.models import Pedido, DetallePedido
from usuarios.models import Cliente
from productos.models import Producto

class Remision(models.Model):
    id_remision = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"Remisión {self.id_remision} - {self.producto.nombre}"

class ReciboObra(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_USO', 'En Uso'),
        ('DEVUELTO', 'Devuelto'),
        ('DANADO', 'Dañado'),
        ('PERDIDO', 'Perdido'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='recibos_obra')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE,
        null=True,  # Permitir nulo temporalmente
        blank=True  # Permitir nulo temporalmente
    )
    detalle_pedido = models.ForeignKey(
        DetallePedido, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='recibos_obra'
    )
    cantidad_solicitada = models.PositiveIntegerField()
    cantidad_vuelta = models.PositiveIntegerField(default=0)
    cantidad_buen_estado = models.PositiveIntegerField(default=0, help_text="Cantidad de productos devueltos en buen estado")
    cantidad_danados = models.PositiveIntegerField(default=0, help_text="Cantidad de productos devueltos con daños")
    cantidad_inservibles = models.PositiveIntegerField(default=0, help_text="Cantidad de productos devueltos inservibles")
    fecha_entrega = models.DateTimeField(default=timezone.now)  # Cambiado de auto_now_add a default
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='PENDIENTE')
    notas_entrega = models.TextField(blank=True, null=True)
    notas_devolucion = models.TextField(blank=True, null=True)
    firmado_cliente = models.BooleanField(default=False)
    firmado_empleado = models.BooleanField(default=False)
    empleado = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, related_name='recibos_generados')
    condicion_entrega = models.TextField(
        help_text='Estado del equipo al momento de la entrega',
        default='Equipo en buen estado al momento de la entrega',
        blank=True
    )
    condicion_devolucion = models.TextField(null=True, blank=True, help_text='Estado del equipo al momento de la devolución')

    class Meta:
        verbose_name = "Recibo de Obra"
        verbose_name_plural = "Recibos de Obra"
        ordering = ['-fecha_entrega']

    def __str__(self):
        if self.producto:
            return f"Recibo de Obra #{self.id} - {self.cliente.usuario.get_full_name()} - {self.producto.nombre}"
        else:
            return f"Recibo de Obra #{self.id} - {self.cliente.usuario.get_full_name()}"

    def get_estado_display(self):
        return dict(self.ESTADO_CHOICES)[self.estado]

    @property
    def esta_completo(self):
        return self.cantidad_vuelta == self.cantidad_solicitada

    @property
    def cantidad_pendiente(self):
        return self.cantidad_solicitada - self.cantidad_vuelta


class DetalleReciboObra(models.Model):
    """Modelo para manejar múltiples productos en un único recibo de obra"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_USO', 'En Uso'),
        ('DEVUELTO', 'Devuelto'),
        ('DANADO', 'Dañado'),
        ('PERDIDO', 'Perdido'),
    ]
    
    recibo = models.ForeignKey(ReciboObra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    detalle_pedido = models.ForeignKey(
        DetallePedido, 
        on_delete=models.CASCADE,
        related_name='detalles_recibos'
    )
    cantidad_solicitada = models.PositiveIntegerField()
    cantidad_vuelta = models.PositiveIntegerField(default=0)
    cantidad_buen_estado = models.PositiveIntegerField(default=0)
    cantidad_danados = models.PositiveIntegerField(default=0)
    cantidad_inservibles = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='PENDIENTE')
    condicion_entrega = models.TextField(blank=True, null=True)
    condicion_devolucion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad_solicitada}) - Recibo #{self.recibo.id}"
    
    @property
    def esta_completo(self):
        return self.cantidad_vuelta == self.cantidad_solicitada
    
    @property
    def cantidad_pendiente(self):
        return self.cantidad_solicitada - self.cantidad_vuelta
