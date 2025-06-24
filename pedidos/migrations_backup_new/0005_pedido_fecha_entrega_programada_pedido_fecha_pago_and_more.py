from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0004_pedido_metodo_pago_pedido_ref_pago_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='fecha_entrega_programada',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_pago',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
