# productos/models.py

from django.db import models, transaction
from decimal import Decimal, ROUND_HALF_UP # Importar Decimal y ROUND_HALF_UP

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio_diario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Precio por día',
        help_text='Precio de renta por día en pesos',
        default=0
    )
    dias_minimos_renta = models.PositiveIntegerField(
        default=1,
        verbose_name='Días mínimos de renta',
        help_text='Número mínimo de días consecutivos que se debe rentar este producto'
    )
    peso = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name='Peso individual (kg)',
        help_text='Peso en kilogramos de una unidad del producto'
    )
    cantidad_disponible = models.PositiveIntegerField()
    cantidad_reservada = models.PositiveIntegerField(default=0)
    cantidad_en_renta = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def get_precio_total(self, dias_renta, cantidad=1):
        """Calcula el precio total para una cantidad de días específica"""
        if dias_renta % self.dias_minimos_renta != 0:
            raise ValueError(f"Los días de renta deben ser múltiplos de {self.dias_minimos_renta}")
        
        return (self.precio_diario * Decimal(str(dias_renta)) * Decimal(str(cantidad))).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    def get_opciones_dias_renta(self, max_dias=90):
        """Retorna las opciones válidas de días de renta hasta el máximo especificado"""
        opciones = []
        dias = self.dias_minimos_renta
        while dias <= max_dias:
            opciones.append(dias)
            dias += self.dias_minimos_renta
        return opciones
    
    def get_precio_display(self):
        """Obtiene el precio formateado para mostrar"""
        return f"${self.precio_diario:,.2f}/día (mín. {self.dias_minimos_renta} día{'s' if self.dias_minimos_renta > 1 else ''})"
    
    def es_dias_valido(self, dias):
        """Verifica si la cantidad de días es válida para este producto"""
        return dias > 0 and dias % self.dias_minimos_renta == 0

    def save(self, *args, **kwargs):
        # Validar que días mínimos sea al menos 1
        if self.dias_minimos_renta < 1:
            self.dias_minimos_renta = 1
        
        super().save(*args, **kwargs)

    def cantidad_total(self):
        return self.cantidad_disponible + self.cantidad_reservada + self.cantidad_en_renta

    def reservar(self, cantidad):
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_disponible:
                producto_a_actualizar.cantidad_disponible -= cantidad
                producto_a_actualizar.cantidad_reservada += cantidad
                producto_a_actualizar.save()
                return True
        return False

    def confirmar_renta(self, cantidad):
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_reservada:
                producto_a_actualizar.cantidad_reservada -= cantidad
                producto_a_actualizar.cantidad_en_renta += cantidad
                producto_a_actualizar.save()
                return True
        return False

    def cancelar_reserva(self, cantidad):
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_reservada:
                producto_a_actualizar.cantidad_reservada -= cantidad # O quantity? Asegúrate de la variable correcta
                producto_a_actualizar.cantidad_disponible += cantidad # O quantity? Asegúrate de la variable correcta
                producto_a_actualizar.save()
                return True
        return False

    def devolver_de_renta(self, cantidad):
        with transaction.atomic():
            producto_a_actualizar = Producto.objects.select_for_update().get(pk=self.pk)
            if cantidad <= producto_a_actualizar.cantidad_en_renta:
                producto_a_actualizar.cantidad_en_renta -= cantidad
                producto_a_actualizar.cantidad_disponible += cantidad
                producto_a_actualizar.save()
                return True
        return False