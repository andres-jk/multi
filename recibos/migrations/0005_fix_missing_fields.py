from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recibos', '0003_estadoproductoindividual'),
        ('pedidos', '0004_populate_required_fields'),
    ]

    operations = [
        # Asegurar que los campos faltantes en DetallePedido estén presentes
        migrations.AlterField(
            model_name='detallereciboobra',
            name='cantidad_buen_estado',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos devueltos en buen estado'),
        ),
        migrations.AlterField(
            model_name='detallereciboobra',
            name='cantidad_danados',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos devueltos con daños'),
        ),
        migrations.AlterField(
            model_name='detallereciboobra',
            name='cantidad_inservibles',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos devueltos inservibles'),
        ),
        migrations.AlterField(
            model_name='detallereciboobra',
            name='cantidad_vuelta',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
