# Generated manually to fix missing fields

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('recibos', '0001_initial'),
    ]

    operations = [
        # Actualizar el modelo DetalleReciboObra para incluir los campos faltantes
        migrations.AddField(
            model_name='detallereciboobra',
            name='cantidad_buen_estado',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos devueltos en buen estado'),
        ),
        migrations.AddField(
            model_name='detallereciboobra',
            name='cantidad_danados',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos devueltos con daños'),
        ),
        migrations.AddField(
            model_name='detallereciboobra',
            name='cantidad_inservibles',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos devueltos inservibles'),
        ),
        migrations.AddField(
            model_name='detallereciboobra',
            name='cantidad_vuelta',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
