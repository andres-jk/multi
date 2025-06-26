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
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='recibos_obra')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_entrega = models.DateTimeField(default=timezone.now)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
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
        return f"Recibo de Obra #{self.id} - {self.cliente.usuario.get_full_name()}"

    @property
    def estado_general(self):
        """Estado general del recibo basado en los detalles"""
        detalles = self.detalles.all()
        if not detalles.exists():
            return "VACIO"
        
        if all(d.estado == 'DEVUELTO' for d in detalles):
            return "DEVUELTO"
        
        if any(d.estado == 'EN_USO' for d in detalles):
            return "EN_USO"

        return "PENDIENTE"

    @property
    def producto(self):
        """Producto principal para compatibilidad con recibos simples"""
        primer_detalle = self.detalles.first()
        return primer_detalle.producto if primer_detalle else None
    
    @property
    def cantidad_solicitada(self):
        """Cantidad total solicitada para compatibilidad"""
        return sum(d.cantidad_solicitada for d in self.detalles.all())
    
    @property
    def cantidad_vuelta(self):
        """Cantidad total devuelta para compatibilidad"""
        return sum(d.cantidad_vuelta for d in self.detalles.all())
    
    @property
    def cantidad_pendiente(self):
        """Cantidad total pendiente"""
        return self.cantidad_solicitada - self.cantidad_vuelta
    
    @property
    def esta_completo(self):
        """Verifica si el recibo está completo"""
        detalles = self.detalles.all()
        if detalles.exists():
            return all(d.esta_completo for d in detalles)
        return False

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
    cantidad_buen_estado = models.PositiveIntegerField(default=0, help_text="Cantidad de productos devueltos en buen estado")
    cantidad_danados = models.PositiveIntegerField(default=0, help_text="Cantidad de productos devueltos con daños")
    cantidad_inservibles = models.PositiveIntegerField(default=0, help_text="Cantidad de productos devueltos inservibles")
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='PENDIENTE')

    class Meta:
        verbose_name = "Detalle de Recibo de Obra"
        verbose_name_plural = "Detalles de Recibos de Obra"

    def __str__(self):
        return f"Detalle de Recibo #{self.recibo.id} - {self.producto.nombre}"

    def get_estado_display(self):
        return dict(self.ESTADO_CHOICES)[self.estado]

    @property
    def esta_completo(self):
        return self.cantidad_vuelta == self.cantidad_solicitada

    @property
    def cantidad_pendiente(self):
        return self.cantidad_solicitada - self.cantidad_vuelta

class EstadoProductoIndividual(models.Model):
    """Modelo para gestionar el estado individual de cada producto en un recibo de obra"""
    ESTADO_CHOICES = [
        ('BUEN_ESTADO', 'Buen Estado'),
        ('PARA_REPARACION', 'Para Reparación'),
        ('INUTILIZABLE', 'Inutilizable'),
    ]
    
    detalle_recibo = models.ForeignKey('DetalleReciboObra', on_delete=models.CASCADE, related_name='estados_individuales')
    numero_serie = models.CharField(max_length=100, blank=True, null=True, help_text="Número de serie o identificación del producto")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BUEN_ESTADO')
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones sobre el estado del producto")
    fecha_revision = models.DateTimeField(default=timezone.now)
    revisado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Estado Individual de Producto"
        verbose_name_plural = "Estados Individuales de Productos"
        ordering = ['-fecha_revision']
    
    def __str__(self):
        return f"{self.detalle_recibo.producto.nombre} - {self.get_estado_display()}"
