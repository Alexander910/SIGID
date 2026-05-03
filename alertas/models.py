"""
Modelo de Alertas del sistema.
"""
from django.db import models
from inventario.models import Product


class Alert(models.Model):
    """Alerta generada automáticamente por el sistema."""

    TYPE_CHOICES = [
        ('sin_stock', 'Sin Stock'),
        ('stock_bajo', 'Stock Bajo'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Producto',
    )
    alert_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=TYPE_CHOICES,
        default='sin_stock',
    )
    message = models.TextField('Mensaje')
    is_read = models.BooleanField('Leída', default=False)
    created_at = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created_at']

    def __str__(self):
        status = '✓' if self.is_read else '⚠'
        return f'{status} {self.product.name} — {self.get_alert_type_display()}'
