"""
Capa de servicios del Inventario.
Lógica de negocio separada de modelos y vistas.
"""
from django.db import models as db_models

from .models import Product


def get_department_products(user):
    """
    Retorna los productos filtrados por departamento del usuario.
    Admins ven todos los productos.
    """
    if user.role == 'admin':
        return Product.objects.select_related('category', 'department').all()
    return Product.objects.select_related('category', 'department').filter(
        department=user.department
    )


def get_low_stock_products(user):
    """
    Retorna productos con stock bajo o en cero para el departamento del usuario.
    """
    qs = get_department_products(user)
    return qs.filter(quantity__lte=db_models.F('min_stock'))


def get_inventory_summary(user):
    """
    Retorna estadísticas resumidas del inventario.
    """
    products = get_department_products(user)
    total = products.count()
    out_of_stock = products.filter(quantity=0).count()
    low_stock = products.filter(
        quantity__gt=0, quantity__lte=db_models.F('min_stock')
    ).count()

    return {
        'total_products': total,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'in_stock': total - out_of_stock,
    }
