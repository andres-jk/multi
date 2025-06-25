from django.db import models, transaction

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)  # Nuevo campo
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_renta = models.CharField(max_length=50)
    cantidad_disponible = models.PositiveIntegerField()
    cantidad_reservada = models.PositiveIntegerField(default=0)
    cantidad_en_renta = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre
        
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
