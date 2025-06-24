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
        migrations.AddField(
            model_name='pedido',
            name='fecha_vencimiento',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_devolucion_programada',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_devolucion_real',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='dias_retraso',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pedido',
            name='cargo_extra_retraso',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='pedido',
            name='ultimo_recordatorio',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='dias_para_recordatorio',
            field=models.IntegerField(default=5, help_text='Días antes del vencimiento para enviar recordatorio'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='recordatorios_enviados',
            field=models.IntegerField(default=0),
        ),
    ]
