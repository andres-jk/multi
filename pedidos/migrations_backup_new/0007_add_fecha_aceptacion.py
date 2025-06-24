from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0006_add_tracking_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='fecha_aceptacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
