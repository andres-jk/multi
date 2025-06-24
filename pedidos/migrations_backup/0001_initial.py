from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id_pedido', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('estado_pedido_general', models.CharField(choices=[('pendiente_pago', 'Pendiente de Pago'), ('pagado', 'Pagado'), ('verificando_pago', 'Verificando Pago'), ('pago_aceptado', 'Pago Aceptado'), ('en_empaque', 'En Proceso de Empaque'), ('en_ruta', 'En Ruta de Entrega'), ('entregado', 'Entregado'), ('en_uso', 'En Uso'), ('programado_devolucion', 'Programado para Devolución'), ('vencido', 'Vencido'), ('recogido', 'Recogido'), ('cancelado', 'Cancelado')], default='pendiente_pago', max_length=30)),
                ('direccion_entrega', models.CharField(max_length=255)),
                ('dias_para_recordatorio', models.IntegerField(default=5, help_text='Días antes del vencimiento para enviar recordatorio')),    
                ('recordatorios_enviados', models.IntegerField(default=0)),
                ('ultimo_recordatorio', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
