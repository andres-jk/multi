from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pedidos', '0013_entregapedido_fecha_entrega_and_more'),  # Updated to use the latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='detallepedido',
            name='cantidad_devuelta',
            field=models.PositiveIntegerField(default=0, help_text='Cantidad de productos que ya han sido devueltos'),
        ),
        migrations.AddField(
            model_name='detallepedido',
            name='renta_extendida',
            field=models.BooleanField(default=False, help_text='Indica si la renta ha sido extendida para los productos restantes'),
        ),
        migrations.AlterField(
            model_name='detallepedido',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('en_preparacion', 'En Preparación'), ('listo_entrega', 'Listo para Entrega'), ('entregado', 'Entregado'), ('devuelto_parcial', 'Devuelto Parcialmente'), ('devuelto', 'Devuelto'), ('cancelado', 'Cancelado')], default='pendiente', max_length=50),
        ),
        migrations.CreateModel(
            name='DevolucionParcial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(help_text='Cantidad de productos devueltos en esta devolución')),
                ('estado', models.CharField(choices=[('buen_estado', 'Buen Estado'), ('danado', 'Dañado'), ('inservible', 'Inservible')], default='buen_estado', max_length=20)),
                ('fecha_devolucion', models.DateTimeField(auto_now_add=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('detalle_pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devoluciones', to='pedidos.detallepedido')),
                ('procesado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devoluciones_procesadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Devolución Parcial',
                'verbose_name_plural': 'Devoluciones Parciales',
                'ordering': ['-fecha_devolucion'],
            },
        ),
        migrations.CreateModel(
            name='ExtensionRenta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_extension', models.DateTimeField(auto_now_add=True)),
                ('dias_adicionales', models.PositiveIntegerField(help_text='Días adicionales de renta')),
                ('cantidad', models.PositiveIntegerField(help_text='Cantidad de productos para los que se extiende la renta')),
                ('precio_diario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('detalle_pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extensiones', to='pedidos.detallepedido')),
                ('procesado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='extensiones_procesadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Extensión de Renta',
                'verbose_name_plural': 'Extensiones de Renta',
                'ordering': ['-fecha_extension'],
            },
        ),
    ]
