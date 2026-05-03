"""
Signals de Movimientos.
Dispara alertas automáticas cuando el stock de un producto llega a 0.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Movement


@receiver(post_save, sender=Movement)
def check_stock_alert(sender, instance, created, **kwargs):
    """
    Después de crear un movimiento, verifica si el producto
    quedó sin stock y genera una alerta.
    """
    if not created:
        return

    product = instance.product

    if product.quantity <= 0:
        from alertas.models import Alert

        # Evitar duplicados: solo crear si no hay alerta activa
        existing = Alert.objects.filter(
            product=product,
            is_read=False,
        ).exists()

        if not existing:
            Alert.objects.create(
                product=product,
                alert_type='sin_stock',
                message=(
                    f'El producto "{product.name}" ({product.code}) '
                    f'se ha quedado sin stock.'
                ),
            )
