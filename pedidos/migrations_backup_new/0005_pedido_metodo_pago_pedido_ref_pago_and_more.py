from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0004_detalle_pedido'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='metodo_pago',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='ref_pago',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
