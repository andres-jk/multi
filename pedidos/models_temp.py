from django.db import models
from usuarios.models import Cliente

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente}"
