from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0004_populate_required_fields'),
    ]

    operations = [
        # Agregar campo ref_pago al modelo Pedido
        migrations.AddField(
            model_name='pedido',
            name='ref_pago',
            field=models.CharField(
                max_length=100, 
                null=True, 
                blank=True, 
                help_text="Referencia del pago"
            ),
        ),
        # Actualizar el campo estado en Pedido para incluir 'CERRADO'
        migrations.AlterField(
            model_name='pedido',
            name='estado_pedido_general',
            field=models.CharField(
                choices=[
                    ('pendiente_pago', 'Pendiente de Pago'),
                    ('procesando_pago', 'Procesando Pago'),
                    ('pagado', 'Pagado'),
                    ('pago_vencido', 'Pago Vencido'),
                    ('pago_rechazado', 'Pago Rechazado'),
                    ('en_preparacion', 'En Preparación'),
                    ('listo_entrega', 'Listo para Entrega'),
                    ('entregado', 'Entregado'),
                    ('programado_devolucion', 'Programado para Devolución'),
                    ('cancelado', 'Cancelado'),
                    ('CERRADO', 'Cerrado'),
                ],
                default='pendiente_pago',
                max_length=50
            ),
        ),
        # Actualizar el campo estado en DetallePedido con las opciones correctas
        migrations.AlterField(
            model_name='detallepedido',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('en_preparacion', 'En Preparación'),
                    ('listo_entrega', 'Listo para Entrega'),
                    ('entregado', 'Entregado'),
                    ('devuelto', 'Devuelto'),
                    ('cancelado', 'Cancelado'),
                ],
                default='pendiente',
                max_length=50
            ),
        ),
    ]
