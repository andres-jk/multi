from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0005_pedido_fecha_entrega_programada_pedido_fecha_pago_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='estado_seguimiento',
            field=models.CharField(choices=[('pendiente', 'Pendiente de Procesar'), ('empacando', 'Empacando Productos'), ('en_ruta_entrega', 'En Ruta de Entrega'), ('entregado', 'Entregado al Cliente'), ('en_uso', 'En Uso por el Cliente'), ('programado_recoleccion', 'Programado para Recolección'), ('en_ruta_recoleccion', 'En Ruta de Recolección'), ('recolectado', 'Recolectado'), ('completado', 'Completado')], default='pendiente', max_length=30),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_empaque_inicio',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_empaque_fin',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_salida_entrega',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_entrega_estimada',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_entrega_real',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='duracion_renta',
            field=models.IntegerField(default=1, help_text='Duración de la renta en meses'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_inicio_renta',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
