"""
Modelo de Movimientos de inventario (entradas y salidas).
"""
from django.conf import settings
from django.db import models
from inventario.models import Product


class Movement(models.Model):
    """Registro de movimiento de stock."""

    TYPE_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Producto',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='movements',
        verbose_name='Responsable',
    )
    type = models.CharField(
        'Tipo',
        max_length=10,
        choices=TYPE_CHOICES,
    )
    quantity = models.PositiveIntegerField('Cantidad')
    observation = models.TextField('Observación', blank=True)
    created_at = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.get_type_display()} — {self.product.name} '
            f'x{self.quantity} ({self.created_at:%d/%m/%Y %H:%M})'
        )
