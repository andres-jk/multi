# Generated by Django 4.2.23 on 2025-06-26 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0007_detallepedido_periodo_renta_detallepedido_tipo_renta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detallepedido',
            name='periodo_renta',
        ),
        migrations.RemoveField(
            model_name='detallepedido',
            name='tipo_renta',
        ),
    ]
