# Generated manually on 2025-06-25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recibos', '0002_alter_detallereciboobra_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoProductoIndividual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_serie', models.CharField(blank=True, help_text='Número de serie o identificación del producto', max_length=100, null=True)),
                ('estado', models.CharField(choices=[('BUEN_ESTADO', 'Buen Estado'), ('PARA_REPARACION', 'Para Reparación'), ('INUTILIZABLE', 'Inutilizable')], default='BUEN_ESTADO', max_length=20)),
                ('observaciones', models.TextField(blank=True, help_text='Observaciones sobre el estado del producto', null=True)),
                ('fecha_revision', models.DateTimeField(default=django.utils.timezone.now)),
                ('detalle_recibo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estados_individuales', to='recibos.detallereciboobra')),
                ('revisado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Estado Individual de Producto',
                'verbose_name_plural': 'Estados Individuales de Productos',
                'ordering': ['-fecha_revision'],
            },
        ),
    ]
