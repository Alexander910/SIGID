"""
Capa de servicios para Movimientos.
Toda la lógica de negocio de entradas/salidas vive aquí.
"""
from django.db import transaction
from .models import Movement


def create_movement(product, user, type, quantity, observation=''):
    """
    Crea un movimiento y actualiza el stock del producto.

    Args:
        product: instancia de Product.
        user: instancia de User (responsable).
        type: 'entrada' o 'salida'.
        quantity: cantidad a mover (positivo).
        observation: texto opcional.

    Returns:
        Movement creado.

    Raises:
        ValueError: si stock insuficiente para salida.
    """
    if quantity <= 0:
        raise ValueError('La cantidad debe ser mayor a cero.')

    if type == 'salida' and product.quantity < quantity:
        raise ValueError(
            f'Stock insuficiente. Disponible: {product.quantity}, '
            f'solicitado: {quantity}.'
        )

    with transaction.atomic():
        if type == 'entrada':
            product.quantity += quantity
        else:
            product.quantity -= quantity

        product.save(update_fields=['quantity', 'updated_at'])

        movement = Movement.objects.create(
            product=product,
            user=user,
            type=type,
            quantity=quantity,
            observation=observation,
        )

    return movement
