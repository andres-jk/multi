from django.db import models, transaction

class Producto(models.Model):
    TIPO_RENTA_CHOICES = [
        ('mensual', 'Mensual'),
        ('semanal', 'Semanal'),
    ]
    
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)  # Nuevo campo
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio mensual')
    precio_semanal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name='Precio semanal'
    )
    peso = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name='Peso individual (kg)',
        help_text='Peso en kilogramos de una unidad del producto'
    )
    tipo_renta = models.CharField(
        max_length=10,
        choices=TIPO_RENTA_CHOICES,
        default='mensual',
        verbose_name='Tipo de renta'
    )
    cantidad_disponible = models.PositiveIntegerField()
    cantidad_reservada = models.PositiveIntegerField(default=0)
    cantidad_en_renta = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    def get_precio_por_tipo(self, tipo_renta='mensual'):
        """Retorna el precio según el tipo de renta"""
        if tipo_renta == 'semanal':
            # Si no hay precio semanal definido, calcularlo como precio_mensual / 4
            if self.precio_semanal:
                return self.precio_semanal
            else:
                return round(self.precio / 4, 2)
        else:
            return self.precio
    
    def save(self, *args, **kwargs):
        """Calcula precio semanal automáticamente si no está definido"""
        if not self.precio_semanal and self.precio:
            try:
                # Convertir a Decimal para evitar errores de tipo
                from decimal import Decimal
                precio_decimal = Decimal(str(self.precio))
                self.precio_semanal = round(precio_decimal / 4, 2)
            except (ValueError, TypeError):
                # Si hay error en la conversión, no calcular precio semanal
                pass
        super().save(*args, **kwargs)
        
    def cantidad_total(self):
        """Retorna la cantidad total de unidades del producto (disponibles + reservadas + en_renta)"""
        return self.cantidad_disponible + self.cantidad_reservada + self.cantidad_en_renta
    
    def reservar(self, cantidad):
        """Reserva una cantidad del producto, moviéndola de disponible a reservada"""
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_disponible:
                producto_a_actualizar.cantidad_disponible -= cantidad
                producto_a_actualizar.cantidad_reservada += cantidad
                producto_a_actualizar.save()
                return True
        return False
    
    def confirmar_renta(self, cantidad):
        """Confirma la renta de una cantidad que estaba reservada"""
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_reservada:
                producto_a_actualizar.cantidad_reservada -= cantidad
                producto_a_actualizar.cantidad_en_renta += cantidad
                producto_a_actualizar.save()
                return True
        return False
    
    def cancelar_reserva(self, cantidad):
        """Cancela la reserva de una cantidad, devolviéndola al estado disponible"""
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_reservada:
                producto_a_actualizar.cantidad_reservada -= cantidad
                producto_a_actualizar.cantidad_disponible += cantidad
                producto_a_actualizar.save()
                return True
        return False
    
    def devolver_de_renta(self, cantidad):
        """Devuelve productos que estaban en renta al estado disponible"""
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_en_renta:
                producto_a_actualizar.cantidad_en_renta -= cantidad
                producto_a_actualizar.cantidad_disponible += cantidad
                producto_a_actualizar.save()
                return True
        return False
