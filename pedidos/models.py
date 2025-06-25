from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from django.conf import settings

class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('pendiente_pago', 'Pendiente de Pago'),
        ('procesando_pago', 'Procesando Pago'),
        ('pagado', 'Pagado'),
        ('pago_vencido', 'Pago Vencido'),
        ('pago_rechazado', 'Pago Rechazado'),
        ('en_preparacion', 'En Preparación'),
        ('listo_entrega', 'Listo para Entrega'),
        ('entregado', 'Entregado'),
        ('programado_devolucion', 'Programado para Devolución'),
        ('cancelado', 'Cancelado')
    )
    
    id_pedido = models.AutoField(primary_key=True)
    cliente = models.ForeignKey('usuarios.Cliente', on_delete=models.CASCADE, null=True, blank=True)  # Keep nullable for now
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_limite_pago = models.DateTimeField(null=True, blank=True)  # Keep nullable for now
    estado_pedido_general = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente_pago')
    direccion_entrega = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_transporte = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    duracion_renta = models.IntegerField(default=1)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    fecha_devolucion_programada = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.estado_pedido_general == 'pagado' and not self.fecha_pago:
            raise ValidationError('Un pedido pagado debe tener fecha de pago.')
    
    def update_total(self):
        iva_rate = Decimal('0.19')
        self.iva = (self.subtotal * iva_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.total = (self.subtotal + self.iva + self.costo_transporte).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        if not self.id_pedido:
            self.fecha_limite_pago = timezone.now() + timedelta(hours=24)
        self.update_total()
        self.full_clean()
        super().save(*args, **kwargs)

    def esta_vencido_pago(self):
        return (self.estado_pedido_general == 'pendiente_pago' and 
                timezone.now() > self.fecha_limite_pago)
    
    def get_tiempo_restante_pago(self):
        if self.estado_pedido_general != 'pendiente_pago':
            return None
        tiempo_restante = self.fecha_limite_pago - timezone.now()
        return tiempo_restante if tiempo_restante.total_seconds() > 0 else None

    @property
    def fecha_vencimiento(self):
        if self.fecha_pago and self.duracion_renta:
            # This is a simple calculation, you might need to adjust it
            # based on how you want to handle months (e.g., using dateutil.relativedelta)
            return self.fecha_pago + timedelta(days=30 * self.duracion_renta)
        return None

    def procesar_pago(self, metodo_pago):
        """
        Procesa el pago del pedido y actualiza su estado
        """
        if metodo_pago.monto != self.total:
            raise ValidationError('El monto del pago no coincide con el total del pedido')
            
        if self.estado_pedido_general not in ['pendiente_pago', 'pago_vencido', 'pago_rechazado']:
            raise ValidationError('El pedido no está en un estado válido para procesar el pago')
            
        with transaction.atomic():
            if metodo_pago.estado == 'aprobado':
                self.estado_pedido_general = 'pagado'
                self.fecha_pago = timezone.now()
                self.metodo_pago = metodo_pago.tipo
                
                # Confirmar la reserva de productos
                detalles = self.detalles.all()
                for detalle in detalles:
                    if not detalle.producto.confirmar_renta(detalle.cantidad):
                        raise ValidationError(f'No hay suficiente stock de {detalle.producto.nombre}')
                
                self.save()
                return True
            elif metodo_pago.estado == 'rechazado':
                self.estado_pedido_general = 'pago_rechazado'
                
                # Liberar productos reservados
                detalles = self.detalles.all()
                for detalle in detalles:
                    detalle.producto.liberar_reserva(detalle.cantidad)
                
                self.save()
                return False
        return False

    def check_vencimiento(self):
        """
        Verifica si el pedido está vencido y actualiza su estado
        """
        if self.estado_pedido_general == 'pendiente_pago' and self.esta_vencido_pago():
            with transaction.atomic():
                self.estado_pedido_general = 'pago_vencido'
                
                # Liberar productos reservados
                detalles = self.detalles.all()
                for detalle in detalles:
                    detalle.producto.liberar_reserva(detalle.cantidad)
                
                self.save()
                return True
        return False

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente.usuario.get_full_name()}"
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    meses_renta = models.PositiveIntegerField(default=1)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=50, default='pendiente')
    notas = models.TextField(blank=True, null=True)

    def clean(self):
        if self.cantidad < 1:
            raise ValidationError('La cantidad debe ser mayor a 0.')
        if self.meses_renta < 1:
            raise ValidationError('El período de renta debe ser al menos 1 mes.')
        if self.producto.cantidad_disponible < self.cantidad:
            raise ValidationError(f'No hay suficiente stock. Disponible: {self.producto.cantidad_disponible}')
            
    def save(self, *args, **kwargs):
        # Calcular subtotal antes de guardar
        self.subtotal = self.precio_unitario * self.cantidad * self.meses_renta
        # Validar los datos
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - {self.meses_renta} meses"

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
