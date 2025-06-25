from django.db import models

class Departamento(models.Model):
    codigo = models.CharField(max_length=2, unique=True, help_text="Código DIVIPOLA del departamento")
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class Municipio(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='municipios')
    codigo = models.CharField(max_length=5, unique=True, help_text="Código DIVIPOLA del municipio")
    nombre = models.CharField(max_length=100)
    costo_transporte = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        help_text="Costo de transporte para este municipio."
    )

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def get_codigo_completo(self):
        return f"{self.departamento.codigo}{self.codigo[2:]}"
