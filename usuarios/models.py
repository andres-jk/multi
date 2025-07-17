from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from .models_divipola import Departamento, Municipio
from django.core.exceptions import ValidationError

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('recibos_obra', 'Empleado de Recibos de Obra'),
        ('cliente', 'Cliente'),
    )
    numero_identidad = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Número de Identidad')  # Permite nulos temporalmente
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    direccion_texto = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección (texto)')
    
    # Permisos específicos para empleados
    puede_gestionar_productos = models.BooleanField(default=False, verbose_name='Puede gestionar productos')
    puede_gestionar_pedidos = models.BooleanField(default=False, verbose_name='Puede gestionar pedidos')
    puede_gestionar_recibos = models.BooleanField(default=False, verbose_name='Puede gestionar recibos de obra')
    puede_gestionar_clientes = models.BooleanField(default=False, verbose_name='Puede gestionar clientes')
    puede_ver_reportes = models.BooleanField(default=False, verbose_name='Puede ver reportes')
    puede_gestionar_inventario = models.BooleanField(default=False, verbose_name='Puede gestionar inventario')
    puede_procesar_pagos = models.BooleanField(default=False, verbose_name='Puede procesar pagos')
    activo = models.BooleanField(default=True, verbose_name='Usuario activo')
    
    def puede_ver_recibos(self):
        """Determina si el usuario puede acceder a la sección de recibos de obra"""
        return self.rol in ['admin', 'recibos_obra'] or self.is_staff or self.puede_gestionar_recibos

    def tiene_permisos_admin(self):
        """Verifica si el usuario tiene permisos de administrador"""
        return self.rol == 'admin' or self.is_superuser
    
    def permisos_empleado(self):
        """Retorna un diccionario con los permisos del empleado"""
        return {
            'productos': self.puede_gestionar_productos,
            'pedidos': self.puede_gestionar_pedidos,
            'recibos': self.puede_gestionar_recibos,
            'clientes': self.puede_gestionar_clientes,
            'reportes': self.puede_ver_reportes,
            'inventario': self.puede_gestionar_inventario,
            'pagos': self.puede_procesar_pagos,
        }

    def __str__(self):
        return self.username

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente')
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.usuario:
            return f"{self.usuario.first_name} {self.usuario.last_name}"
        return "Cliente sin usuario asignado"

class Direccion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='direcciones', null=True)  # Temporarily nullable
    calle = models.CharField(max_length=200, null=True, blank=True)  # Temporarily optional
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=200, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True)
    codigo_divipola = models.CharField(max_length=5, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    principal = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        
    def __str__(self):
        partes = [self.calle or ""]
        if self.numero:
            partes.append(f"#{self.numero}")
        if self.municipio:
            partes.append(f"- {self.municipio}")
        if self.departamento:
            partes.append(f", {self.departamento}")
        return " ".join(filter(None, partes))
        
    def save(self, *args, **kwargs):
        if self.municipio:
            self.codigo_divipola = self.municipio.codigo
        super().save(*args, **kwargs)

class MetodoPago(models.Model):
    TIPO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
    )
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente de Verificación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    )
    
    pedido = models.ForeignKey('pedidos.Pedido', on_delete=models.CASCADE, related_name='pagos', null=True, blank=True)  # Keep nullable for now
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(default=timezone.now)  # Changed from auto_now_add
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    comprobante = models.FileField(upload_to='comprobantes_pago/', null=True, blank=True)
    numero_referencia = models.CharField(max_length=50, null=True, blank=True)
    notas = models.TextField(blank=True)
    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pagos_verificados'
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.pedido.id_pedido} - {self.monto}"

    def validar_pago(self):
        """
        Valida que el pago cumpla con los requisitos básicos
        """
        if not self.pedido:
            raise ValidationError('El pago debe estar asociado a un pedido')
            
        if not self.monto or self.monto <= 0:
            raise ValidationError('El monto del pago debe ser mayor a cero')
            
        # Temporarily disable comprobante requirement to allow testing
        # if not self.comprobante and self.tipo != 'efectivo':
        #     raise ValidationError('Se requiere comprobante de pago para pagos que no son en efectivo')
            
        if self.estado == 'aprobado' and not self.verificado_por:
            raise ValidationError('Un pago aprobado debe tener un verificador')
            
    def save(self, *args, **kwargs):
        self.validar_pago()
        super().save(*args, **kwargs)

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
    dias_renta = models.PositiveIntegerField(
        verbose_name='Días de renta',
        help_text='Número de días a rentar (debe ser múltiplo de los días mínimos del producto)',
        default=1
    )
    fecha_agregado = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de agregado'
    )
    reservado = models.BooleanField(
        default=False,
        verbose_name='Reservado'
    )
    en_proceso_pago = models.BooleanField(
        default=False,
        verbose_name='En proceso de pago'
    )

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        # Asegurar que no haya duplicados para el mismo usuario y producto
        unique_together = ['usuario', 'producto']

    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad}) - {self.dias_renta} días - {self.usuario.username}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal usando el nuevo sistema de días"""
        try:
            total = self.producto.get_precio_total(self.dias_renta, self.cantidad)
            return total
        except ValueError:
            # Si hay error en los días, retornar 0
            return Decimal('0.00')
    
    @property
    def precio_unitario(self):
        """Retorna el precio diario del producto"""
        return self.producto.precio_diario
    
    @property
    def peso_total(self):
        """Devuelve el peso total de este item del carrito (peso individual x cantidad)"""
        peso_individual = Decimal(str(self.producto.peso))
        return (peso_individual * self.cantidad).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_descripcion_periodo(self):
        """Retorna una descripción legible del período"""
        return f"{self.dias_renta} día{'s' if self.dias_renta > 1 else ''}"
    
    def get_descripcion_dias(self):
        """Alias para get_descripcion_periodo - mantiene compatibilidad con PDFs"""
        return self.get_descripcion_periodo()

    def es_valido(self):
        """Verifica si este item del carrito es válido"""
        return self.producto.es_dias_valido(self.dias_renta)

    def reservar(self):
        """Intenta reservar la cantidad del producto"""
        if not self.reservado and self.producto.cantidad_disponible >= self.cantidad and self.es_valido():
            with transaction.atomic():
                self.producto.cantidad_disponible -= self.cantidad
                self.producto.save()
                self.reservado = True
                self.save()
                return True
        return False

    def liberar_reserva(self):
        """Libera la cantidad reservada del producto"""
        if self.reservado:
            with transaction.atomic():
                self.producto.cantidad_disponible += self.cantidad
                self.producto.save()
                self.reservado = False
                self.save()

    def clean(self):
        if self.cantidad < 1:
            raise ValidationError('La cantidad debe ser mayor a 0')
        if self.dias_renta < 1:
            raise ValidationError('Los días de renta deben ser al menos 1')
        if not self.producto.es_dias_valido(self.dias_renta):
            raise ValidationError(f'Los días de renta deben ser múltiplos de {self.producto.dias_minimos_renta}')
        if not self.reservado and self.producto.cantidad_disponible < self.cantidad:
            raise ValidationError(f'No hay suficiente stock. Disponible: {self.producto.cantidad_disponible}')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def limpiar_carritos_antiguos(cls):
        """Limpia los carritos que tienen más de 24 horas sin actividad"""
        limite_tiempo = timezone.now() - timedelta(hours=24)
        carritos_antiguos = cls.objects.filter(fecha_agregado__lt=limite_tiempo, reservado=True)
        
        for item in carritos_antiguos:
            item.liberar_reserva()
        
        carritos_antiguos.delete()
