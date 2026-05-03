"""
Context processor para mostrar el conteo de alertas en el navbar.
"""


def alertas_count(request):
    """Agrega el conteo de alertas no leídas al contexto de cada template."""
    if not request.user.is_authenticated:
        return {'alertas_count': 0}

    from alertas.models import Alert

    qs = Alert.objects.filter(is_read=False)

    if request.user.role != 'admin':
        qs = qs.filter(product__department=request.user.department)

    return {'alertas_count': qs.count()}
