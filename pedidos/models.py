from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from usuarios.models import Cliente
from productos.models import Producto

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente_pago', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('verificando_pago', 'Verificando Pago'),
        ('pago_aceptado', 'Pago Aceptado'),
        ('en_empaque', 'En Proceso de Empaque'),
        ('en_ruta', 'En Ruta de Entrega'),
        ('entregado', 'Entregado'),
        ('en_uso', 'En Uso'),
        ('programado_devolucion', 'Programado para Devolución'),
        ('vencido', 'Vencido'),
        ('recogido', 'Recogido'),
        ('cancelado', 'Cancelado')
    ]
    
    ESTADO_SEGUIMIENTO_CHOICES = [
        ('pendiente', 'Pendiente de Procesar'),
        ('empacando', 'Empacando Productos'),
        ('en_ruta_entrega', 'En Ruta de Entrega'),
        ('entregado', 'Entregado al Cliente'),
        ('en_uso', 'En Uso por el Cliente'),
        ('programado_recoleccion', 'Programado para Recolección'),
        ('en_ruta_recoleccion', 'En Ruta de Recolección'),
        ('recolectado', 'Recolectado'),
        ('completado', 'Completado')
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(default=timezone.now)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estado_pedido_general = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente_pago')
    estado_seguimiento = models.CharField(max_length=30, choices=ESTADO_SEGUIMIENTO_CHOICES, default='pendiente')
    direccion_entrega = models.CharField(max_length=255, default='')
    notas = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    ref_pago = models.CharField(max_length=100, blank=True, null=True, help_text='Referencia de pago o número de transacción')
    
    # Campos de seguimiento y fechas de proceso
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)
    fecha_empaque_inicio = models.DateTimeField(null=True, blank=True)
    fecha_empaque_fin = models.DateTimeField(null=True, blank=True)
    fecha_salida_entrega = models.DateTimeField(null=True, blank=True)
    fecha_entrega_estimada = models.DateTimeField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    
    # Campos para gestión de devolución
    duracion_renta = models.IntegerField(default=1, help_text='Duración de la renta en meses')
    fecha_inicio_renta = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    fecha_devolucion_programada = models.DateTimeField(null=True, blank=True)
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    dias_retraso = models.IntegerField(default=0)
    cargo_extra_retraso = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Campos para recordatorios y seguimiento
    ultimo_recordatorio = models.DateTimeField(null=True, blank=True)
    dias_para_recordatorio = models.IntegerField(default=5, help_text='Días antes del vencimiento para enviar recordatorio')
    recordatorios_enviados = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        # Si el pedido es aceptado y no tiene fecha de vencimiento calculada
        if self.estado_pedido_general == 'pago_aceptado' and not self.fecha_vencimiento:
            self.fecha_inicio_renta = timezone.now()
            self.fecha_vencimiento = self.fecha_inicio_renta + timedelta(days=30 * self.duracion_renta)
        
        # Calcular días de retraso y cargos extras si aplica
        if self.fecha_vencimiento and timezone.now() > self.fecha_vencimiento:
            dias_retraso = (timezone.now() - self.fecha_vencimiento).days
            self.dias_retraso = dias_retraso
            # Cargo extra por día (10% del total del pedido)
            cargo_por_dia = self.total * Decimal('0.10')
            self.cargo_extra_retraso = cargo_por_dia * Decimal(str(dias_retraso))
        
        super().save(*args, **kwargs)
    
    def calcular_tiempo_restante(self):
        if not self.fecha_vencimiento:
            return None
        tiempo_restante = self.fecha_vencimiento - timezone.now()
        return tiempo_restante if tiempo_restante.total_seconds() > 0 else timedelta(0)
    
    def necesita_recordatorio(self):
        if not self.fecha_vencimiento:
            return False
        dias_faltantes = (self.fecha_vencimiento - timezone.now()).days
        return (dias_faltantes <= self.dias_para_recordatorio and 
                (not self.ultimo_recordatorio or 
                 (timezone.now() - self.ultimo_recordatorio).days >= 1))
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    meses_renta = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.precio_unitario and self.producto:
            self.precio_unitario = self.producto.precio
        self.subtotal = self.precio_unitario * self.cantidad * self.meses_renta
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto} x{self.cantidad} ({self.meses_renta} meses) - Pedido #{self.pedido.id_pedido}"

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"
