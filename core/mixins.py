"""
Mixins reutilizables para el sistema SIGID.
"""
from django.contrib.auth.mixins import LoginRequiredMixin


class DepartmentFilterMixin:
    """
    Filtra automáticamente el queryset según el departamento del usuario.
    Los administradores ven todos los registros.
    Los encargados solo ven registros de su departamento.
    """

    department_field = 'department'  # campo FK al departamento

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role != 'admin':
            filter_kwargs = {self.department_field: user.department}
            qs = qs.filter(**filter_kwargs)

        return qs


class AdminRequiredMixin(LoginRequiredMixin):
    """
    Solo permite acceso a usuarios con rol 'admin'.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'admin':
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(
                '<h1>403 — Acceso denegado</h1>'
                '<p>No tienes permisos para acceder a esta sección.</p>'
            )
        return super().dispatch(request, *args, **kwargs)
