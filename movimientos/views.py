from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import DepartmentFilterMixin
from .models import Movement
from .forms import MovementForm
from .services import create_movement


class MovementListView(
    LoginRequiredMixin, DepartmentFilterMixin, ListView
):
    """Lista de movimientos filtrados por departamento."""
    model = Movement
    template_name = 'movimientos/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20
    department_field = 'product__department'

    def get_queryset(self):
        qs = super().get_queryset().select_related('product', 'user')
        # Filtro por tipo
        type_filter = self.request.GET.get('type')
        if type_filter in ('entrada', 'salida'):
            qs = qs.filter(type=type_filter)
        return qs


class MovementCreateView(LoginRequiredMixin, CreateView):
    """Registrar nuevo movimiento — usa la capa de servicios."""
    model = Movement
    form_class = MovementForm
    template_name = 'movimientos/movement_form.html'
    success_url = reverse_lazy('movimientos:movement_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            create_movement(
                product=form.cleaned_data['product'],
                user=self.request.user,
                type=form.cleaned_data['type'],
                quantity=form.cleaned_data['quantity'],
                observation=form.cleaned_data.get('observation', ''),
            )
            messages.success(self.request, 'Movimiento registrado correctamente.')
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        from django.shortcuts import redirect
        return redirect(self.success_url)
