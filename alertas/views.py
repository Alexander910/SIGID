from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.shortcuts import get_object_or_404, redirect

from core.mixins import DepartmentFilterMixin
from .models import Alert


class AlertListView(LoginRequiredMixin, DepartmentFilterMixin, ListView):
    """Lista de alertas del sistema."""
    model = Alert
    template_name = 'alertas/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 20
    department_field = 'product__department'


class AlertMarkReadView(LoginRequiredMixin, View):
    """Marcar alerta como leída."""

    def post(self, request, pk):
        qs = Alert.objects.all()
        if request.user.role != 'admin':
            qs = qs.filter(product__department=request.user.department)

        alert = get_object_or_404(qs, pk=pk)
        alert.is_read = True
        alert.save(update_fields=['is_read'])
        return redirect('alertas:alert_list')


class AlertMarkAllReadView(LoginRequiredMixin, View):
    """Marcar todas las alertas como leídas."""

    def post(self, request):
        qs = Alert.objects.filter(is_read=False)
        if request.user.role != 'admin':
            qs = qs.filter(product__department=request.user.department)
        qs.update(is_read=True)
        return redirect('alertas:alert_list')
