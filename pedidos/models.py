from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('pendiente_pago', 'Pendiente de Pago'),
        ('procesando_pago', 'Procesando Pago'),
        ('pagado', 'Pagado'),
        ('pago_vencido', 'Pago Vencido'),
        ('pago_rechazado', 'Pago Rechazado'),
        ('en_preparacion', 'En Preparación'),
        ('listo_entrega', 'Listo para Entrega'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('recibido', 'Recibido'),
        ('programado_devolucion', 'Programado para Devolución'),
        ('cancelado', 'Cancelado'),
        ('CERRADO', 'Cerrado'),  # Agregar este estado que se usa en las vistas
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
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Entrega')
    metodo_pago = models.CharField(max_length=50, null=True, blank=True)
    fecha_devolucion_programada = models.DateTimeField(null=True, blank=True)
    # Agregar campo faltante que se usa en las vistas
    ref_pago = models.CharField(max_length=100, null=True, blank=True, help_text="Referencia del pago")

    def clean(self):
        if self.estado_pedido_general == 'pagado' and not self.fecha_pago:
            raise ValidationError('Un pedido pagado debe tener fecha de pago.')
    
    def update_total(self):
        # Solo calcular si el pedido ya tiene ID (para evitar errores en creación)
        if not self.pk:
            return
            
        # Only recalculate if subtotal is 0 or not set (to avoid overriding manually calculated totals)
        if not self.subtotal or self.subtotal == 0:
            # Calculate from detail items if they exist
            if hasattr(self, 'detalles') and self.detalles.exists():
                self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
            
        # Always ensure IVA and total are calculated from current values
        iva_rate = Decimal('0.19')
        calculated_iva = (self.subtotal * iva_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        calculated_total = (self.subtotal + calculated_iva + (self.costo_transporte or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Only update if we don't already have valid values
        if not self.iva or self.iva == 0:
            self.iva = calculated_iva
        if not self.total or self.total == 0:
            self.total = calculated_total

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

    def get_fecha_inicio_renta(self):
        """
        Obtiene la fecha de inicio de la renta (cuando se entregó)
        """
        # Si hay detalles entregados, usar la fecha más temprana
        detalles_entregados = self.detalles.filter(
            estado__in=['entregado'], 
            fecha_entrega__isnull=False
        ).order_by('fecha_entrega').first()
        
        if detalles_entregados:
            return detalles_entregados.fecha_entrega
        
        # Si no hay detalles entregados pero el pedido está pagado, usar fecha de pago + tiempo estimado de preparación
        if self.fecha_pago and self.estado_pedido_general in ['pagado', 'en_preparacion', 'listo_entrega', 'entregado']:
            # Asumir 1-2 días para preparación y entrega
            return self.fecha_pago + timedelta(days=1)
        
        return None

    def get_fecha_fin_renta(self):
        """
        Calcula la fecha cuando debe terminar la renta
        """
        fecha_inicio = self.get_fecha_inicio_renta()
        if not fecha_inicio:
            return None
        
        # Usar la duración máxima de los detalles
        max_dias_renta = max([detalle.dias_renta for detalle in self.detalles.all()], default=self.duracion_renta or 7)
        return fecha_inicio + timedelta(days=max_dias_renta)

    def get_tiempo_restante_renta(self):
        """
        Calcula el tiempo restante de la renta
        """
        fecha_fin = self.get_fecha_fin_renta()
        if not fecha_fin:
            return None
        
        tiempo_restante = fecha_fin - timezone.now()
        return tiempo_restante if tiempo_restante.total_seconds() > 0 else timedelta(0)

    def get_estado_tiempo_renta(self):
        """
        Obtiene el estado del tiempo de renta (normal, próximo a vencer, vencido)
        """
        tiempo_restante = self.get_tiempo_restante_renta()
        if not tiempo_restante:
            return None
        
        dias_restantes = tiempo_restante.days
        
        if tiempo_restante.total_seconds() <= 0:
            return 'vencido'
        elif dias_restantes <= 1:
            return 'vence_hoy'
        elif dias_restantes <= 3:
            return 'vence_pronto'
        else:
            return 'normal'

    def get_tiempo_restante_renta_humanizado(self):
        """
        Devuelve el tiempo restante en formato legible
        """
        tiempo_restante = self.get_tiempo_restante_renta()
        if not tiempo_restante:
            return "No iniciado"
        
        if tiempo_restante.total_seconds() <= 0:
            tiempo_vencido = timezone.now() - self.get_fecha_fin_renta()
            if tiempo_vencido.days > 0:
                return f"Vencido hace {tiempo_vencido.days} días"
            else:
                horas = int(tiempo_vencido.total_seconds() / 3600)
                return f"Vencido hace {horas} horas"
        
        dias = tiempo_restante.days
        horas = int((tiempo_restante.total_seconds() % 86400) / 3600)
        
        if dias > 0:
            if horas > 0:
                return f"{dias} días, {horas} horas"
            else:
                return f"{dias} días"
        elif horas > 0:
            return f"{horas} horas"
        else:
            minutos = int((tiempo_restante.total_seconds() % 3600) / 60)
            return f"{minutos} minutos"

    def debe_notificar_vencimiento(self):
        """
        Determina si se debe notificar sobre el vencimiento próximo
        """
        estado_tiempo = self.get_estado_tiempo_renta()
        return estado_tiempo in ['vence_hoy', 'vence_pronto', 'vencido']

    def get_porcentaje_tiempo_transcurrido(self):
        """
        Calcula el porcentaje del tiempo de renta que ha transcurrido
        """
        fecha_inicio = self.get_fecha_inicio_renta()
        fecha_fin = self.get_fecha_fin_renta()
        
        if not fecha_inicio or not fecha_fin:
            return 0
        
        tiempo_total = fecha_fin - fecha_inicio
        tiempo_transcurrido = timezone.now() - fecha_inicio
        
        if tiempo_total.total_seconds() <= 0:
            return 100
        
        porcentaje = (tiempo_transcurrido.total_seconds() / tiempo_total.total_seconds()) * 100
        return min(100, max(0, porcentaje))

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
            
        if self.estado_pedido_general not in ['pendiente_pago', 'procesando_pago', 'pago_vencido', 'pago_rechazado']:
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
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo_entrega', 'Listo para Entrega'),
        ('entregado', 'Entregado'),
        ('devuelto_parcial', 'Devuelto Parcialmente'),
        ('devuelto', 'Devuelto'),
        ('cancelado', 'Cancelado'),
    ]
    
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio por día', default=0)
    dias_renta = models.PositiveIntegerField(verbose_name='Días de renta', default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, null=True)
    cantidad_devuelta = models.PositiveIntegerField(default=0, help_text="Cantidad de productos que ya han sido devueltos")
    renta_extendida = models.BooleanField(default=False, help_text="Indica si la renta ha sido extendida para los productos restantes")

    @property
    def cantidad_pendiente_devolucion(self):
        """
        Calcula la cantidad de productos pendientes por devolver
        """
        return self.cantidad - self.cantidad_devuelta

    def get_estado_display(self):
        """Método para obtener el display del estado"""
        return dict(self.ESTADO_CHOICES).get(self.estado, self.estado)

    def clean(self):
        if self.cantidad < 1:
            raise ValidationError('La cantidad debe ser mayor a 0.')
        if self.dias_renta < 1:
            raise ValidationError('Los días de renta deben ser al menos 1.')
        if not self.producto.es_dias_valido(self.dias_renta):
            raise ValidationError(f'Los días de renta deben ser múltiplos de {self.producto.dias_minimos_renta}')
        if self.producto.cantidad_disponible < self.cantidad:
            raise ValidationError(f'No hay suficiente stock. Disponible: {self.producto.cantidad_disponible}')
            
    def save(self, *args, **kwargs):
        # Calcular subtotal antes de guardar
        self.subtotal = self.precio_diario * self.cantidad * self.dias_renta
        # Validar los datos
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - {self.dias_renta} días"

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'

    def get_fecha_fin_renta_detalle(self):
        """
        Calcula la fecha de fin de renta para este detalle específico
        """
        if not self.fecha_entrega:
            return None
        return self.fecha_entrega + timedelta(days=self.dias_renta)

    def get_tiempo_restante_renta_detalle(self):
        """
        Calcula el tiempo restante de renta para este detalle
        """
        fecha_fin = self.get_fecha_fin_renta_detalle()
        if not fecha_fin:
            return None
        
        tiempo_restante = fecha_fin - timezone.now()
        return tiempo_restante if tiempo_restante.total_seconds() > 0 else timedelta(0)

    def get_estado_tiempo_renta_detalle(self):
        """
        Obtiene el estado del tiempo de renta para este detalle
        """
        tiempo_restante = self.get_tiempo_restante_renta_detalle()
        if not tiempo_restante:
            return None
        
        dias_restantes = tiempo_restante.days
        
        if tiempo_restante.total_seconds() <= 0:
            return 'vencido'
        elif dias_restantes <= 1:
            return 'vence_hoy'
        elif dias_restantes <= 3:
            return 'vence_pronto'
        else:
            return 'normal'

    def get_tiempo_restante_humanizado_detalle(self):
        """
        Devuelve el tiempo restante en formato legible para este detalle
        """
        tiempo_restante = self.get_tiempo_restante_renta_detalle()
        if not tiempo_restante:
            if self.estado in ['devuelto']:
                return "Devuelto"
            elif self.estado in ['devuelto_parcial']:
                return f"Devuelto parcialmente ({self.cantidad_devuelta}/{self.cantidad})"
            elif self.estado in ['cancelado']:
                return "Cancelado"
            else:
                return "No entregado"
        
        if tiempo_restante.total_seconds() <= 0:
            tiempo_vencido = timezone.now() - self.get_fecha_fin_renta_detalle()
            if tiempo_vencido.days > 0:
                return f"Vencido hace {tiempo_vencido.days} días"
            else:
                horas = int(tiempo_vencido.total_seconds() / 3600)
                return f"Vencido hace {horas} horas"
        
        dias = tiempo_restante.days
        horas = int((tiempo_restante.total_seconds() % 86400) / 3600)
        
        if dias > 0:
            if horas > 0:
                return f"{dias} días, {horas} horas"
            else:
                return f"{dias} días"
        elif horas > 0:
            return f"{horas} horas"
        else:
            minutos = int((tiempo_restante.total_seconds() % 3600) / 60)
            return f"{minutos} minutos"

    def get_costo_total_detalle(self):
        """
        Calcula el costo total para este detalle
        """
        return self.precio_diario * self.cantidad * self.dias_renta
        
    @property
    def cantidad_pendiente_devolucion(self):
        """
        Calcula la cantidad pendiente de devolución
        """
        return self.cantidad - self.cantidad_devuelta


class DevolucionParcial(models.Model):
    """
    Modelo para registrar devoluciones parciales de productos en un pedido
    """
    ESTADO_CHOICES = [
        ('buen_estado', 'Buen Estado'),
        ('danado', 'Dañado'),
        ('inservible', 'Inservible'),
    ]
    
    detalle_pedido = models.ForeignKey(DetallePedido, related_name='devoluciones', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(help_text="Cantidad de productos devueltos en esta devolución")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='buen_estado')
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True)
    procesado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='devoluciones_procesadas')
    
    class Meta:
        verbose_name = 'Devolución Parcial'
        verbose_name_plural = 'Devoluciones Parciales'
        ordering = ['-fecha_devolucion']
        
    def __str__(self):
        return f"Devolución de {self.cantidad} {self.detalle_pedido.producto.nombre} - {self.get_estado_display()}"
    
    def save(self, *args, **kwargs):
        nuevo_registro = not self.pk  # Verificar si es un nuevo registro
        
        # Ejecutar el guardado normal
        super().save(*args, **kwargs)
        
        # Solo actualizar el detalle si es un nuevo registro
        if nuevo_registro:
            # Actualizar el detalle del pedido
            detalle = self.detalle_pedido
            detalle.cantidad_devuelta += self.cantidad
            
            # Actualizar el estado del detalle
            if detalle.cantidad_devuelta >= detalle.cantidad:
                detalle.estado = 'devuelto'
            else:
                detalle.estado = 'devuelto_parcial'
                
            detalle.save()
            
            # Devolver al inventario si está en buen estado
            if self.estado == 'buen_estado':
                self.detalle_pedido.producto.devolver_de_renta(self.cantidad)


class ExtensionRenta(models.Model):
    """
    Modelo para registrar extensiones de renta para productos que han sido devueltos parcialmente
    """
    detalle_pedido = models.ForeignKey(DetallePedido, related_name='extensiones', on_delete=models.CASCADE)
    fecha_extension = models.DateTimeField(auto_now_add=True)
    dias_adicionales = models.PositiveIntegerField(help_text="Días adicionales de renta")
    cantidad = models.PositiveIntegerField(help_text="Cantidad de productos para los que se extiende la renta")
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True, null=True)
    procesado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='extensiones_procesadas')
    
    class Meta:
        verbose_name = 'Extensión de Renta'
        verbose_name_plural = 'Extensiones de Renta'
        ordering = ['-fecha_extension']
        
    def __str__(self):
        return f"Extensión de renta para {self.cantidad} {self.detalle_pedido.producto.nombre} por {self.dias_adicionales} días"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal antes de guardar
        self.subtotal = self.precio_diario * self.cantidad * self.dias_adicionales
        
        # Guardar el objeto
        super().save(*args, **kwargs)
        
        # Actualizar el detalle del pedido
        detalle = self.detalle_pedido
        detalle.renta_extendida = True
        detalle.save()

class EntregaPedido(models.Model):
    """Modelo para gestionar las entregas de pedidos con seguimiento GPS"""
    
    ESTADO_ENTREGA_CHOICES = (
        ('programada', 'Programada'),
        ('en_camino', 'En Camino'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('devuelta', 'Devuelta'),
    )
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='entrega')
    empleado_entrega = models.ForeignKey(
        'usuarios.Usuario', 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 'recibos_obra'},
        verbose_name='Empleado de Entrega'
    )
    
    # Información de programación
    fecha_programada = models.DateTimeField(verbose_name='Fecha Programada')
    fecha_inicio_recorrido = models.DateTimeField(null=True, blank=True, verbose_name='Inicio de Recorrido')
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Entrega')
    fecha_entrega_real = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Entrega Real')
    
    # Información de ubicación
    direccion_salida = models.CharField(max_length=255, verbose_name='Dirección de Salida')
    direccion_destino = models.CharField(max_length=255, verbose_name='Dirección de Destino')
    
    # Coordenadas GPS de seguimiento
    latitud_inicial = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='Latitud Inicial')
    longitud_inicial = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='Longitud Inicial')
    latitud_actual = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud_actual = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    ultima_actualizacion_gps = models.DateTimeField(null=True, blank=True)
    
    # Información del vehículo
    vehiculo_placa = models.CharField(max_length=10, verbose_name='Placa del Vehículo')
    conductor_nombre = models.CharField(max_length=100, verbose_name='Nombre del Conductor')
    conductor_telefono = models.CharField(max_length=15, verbose_name='Teléfono del Conductor')
    
    # Estado y tiempos estimados
    estado_entrega = models.CharField(max_length=20, choices=ESTADO_ENTREGA_CHOICES, default='programada')
    tiempo_estimado_llegada = models.DateTimeField(null=True, blank=True, verbose_name='Tiempo Estimado de Llegada')
    distancia_restante_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Información adicional
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    firma_recepcion = models.ImageField(upload_to='firmas_entrega/', null=True, blank=True)
    foto_entrega = models.ImageField(upload_to='fotos_entrega/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Entrega de Pedido'
        verbose_name_plural = 'Entregas de Pedidos'
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f'Entrega {self.pedido.id_pedido} - {self.get_estado_entrega_display()}'
    
    def get_estado_color(self):
        """Retorna el color asociado al estado de la entrega"""
        colores = {
            'programada': 'secondary',
            'en_camino': 'warning',
            'entregada': 'success',
            'cancelada': 'danger',
            'devuelta': 'info',
        }
        return colores.get(self.estado_entrega, 'secondary')
    
    def get_estado_icon(self):
        """Retorna el icono asociado al estado de la entrega"""
        iconos = {
            'programada': 'fas fa-calendar-alt',
            'en_camino': 'fas fa-truck',
            'entregada': 'fas fa-check-circle',
            'cancelada': 'fas fa-times-circle',
            'devuelta': 'fas fa-undo',
        }
        return iconos.get(self.estado_entrega, 'fas fa-question-circle')
    
    def iniciar_recorrido(self, latitud_inicial=None, longitud_inicial=None):
        """Inicia el recorrido de entrega"""
        self.estado_entrega = 'en_camino'
        self.fecha_inicio_recorrido = timezone.now()
        if latitud_inicial and longitud_inicial:
            self.latitud_inicial = latitud_inicial
            self.longitud_inicial = longitud_inicial
            self.latitud_actual = latitud_inicial
            self.longitud_actual = longitud_inicial
            self.ultima_actualizacion_gps = timezone.now()
        
        # Actualizar estado del pedido
        self.pedido.estado_pedido_general = 'en_camino'
        self.pedido.save()
        self.save()
    
    def actualizar_ubicacion(self, latitud, longitud, tiempo_estimado=None, distancia_restante=None):
        """Actualiza la ubicación GPS del vehículo"""
        self.latitud_actual = latitud
        self.longitud_actual = longitud
        self.ultima_actualizacion_gps = timezone.now()
        
        if tiempo_estimado:
            self.tiempo_estimado_llegada = tiempo_estimado
        if distancia_restante:
            self.distancia_restante_km = distancia_restante
        
        self.save()
    
    def confirmar_entrega(self):
        """Confirma la entrega del pedido"""
        self.estado_entrega = 'entregada'
        self.fecha_entrega = timezone.now()
        self.fecha_entrega_real = timezone.now()
        
        # Actualizar estado del pedido y iniciar contador de devolución
        self.pedido.estado_pedido_general = 'recibido'  # Cambiado a 'recibido' en lugar de 'entregado'
        self.pedido.fecha_entrega = timezone.now()
        self.pedido.save()
        self.save()
    
    def get_tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido desde el inicio del recorrido"""
        if self.fecha_inicio_recorrido:
            return timezone.now() - self.fecha_inicio_recorrido
        return None
    
    @property
    def tiempo_en_ruta(self):
        """Retorna el tiempo en ruta en minutos"""
        tiempo_transcurrido = self.get_tiempo_transcurrido()
        if tiempo_transcurrido:
            return int(tiempo_transcurrido.total_seconds() / 60)
        return 0
    
    def get_tiempo_estimado_restante(self):
        """Retorna el tiempo estimado restante para la entrega"""
        if self.tiempo_estimado_llegada:
            tiempo_restante = self.tiempo_estimado_llegada - timezone.now()
            return tiempo_restante if tiempo_restante.total_seconds() > 0 else None
        return None
    
    def esta_en_tiempo(self):
        """Verifica si la entrega está dentro del tiempo programado"""
        fecha_real = self.fecha_entrega_real or self.fecha_entrega
        if fecha_real and self.fecha_programada:
            return fecha_real <= self.fecha_programada + timedelta(hours=2)
        return True
    
    def get_url_seguimiento(self):
        """Retorna la URL para el seguimiento de la entrega"""
        return reverse('pedidos:seguimiento_entrega', kwargs={'pedido_id': self.pedido.id_pedido})
    
    def get_ubicacion_maps_url(self):
        """Retorna la URL de Google Maps con la ubicación actual"""
        if self.latitud_actual and self.longitud_actual:
            return f"https://maps.google.com/maps?q={self.latitud_actual},{self.longitud_actual}"
        return None
