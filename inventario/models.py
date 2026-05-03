"""
Modelos del Inventario: Categoría y Producto.
"""
from django.db import models
from usuarios.models import Department


class Category(models.Model):
    """Categoría de productos."""

    name = models.CharField('Nombre', max_length=100, unique=True)
    description = models.TextField('Descripción', blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto del inventario."""

    name = models.CharField('Nombre', max_length=200)
    code = models.CharField('Código', max_length=50, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Categoría',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Departamento',
    )
    description = models.TextField('Descripción', blank=True)
    quantity = models.PositiveIntegerField('Cantidad en Stock', default=0)
    min_stock = models.PositiveIntegerField('Stock Mínimo', default=5)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
        unique_together = ['code', 'department']

    def __str__(self):
        return f'{self.code} — {self.name}'

    @property
    def has_stock(self):
        return self.quantity > 0

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock
