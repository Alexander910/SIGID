from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView,
)
from django.urls import reverse_lazy

from core.mixins import DepartmentFilterMixin
from .models import Product
from .forms import ProductForm
from .services import get_inventory_summary


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal del sistema."""
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['summary'] = get_inventory_summary(self.request.user)

        # Últimos movimientos
        from movimientos.models import Movement
        movements_qs = Movement.objects.select_related(
            'product', 'user'
        ).order_by('-created_at')

        if self.request.user.role != 'admin':
            movements_qs = movements_qs.filter(
                product__department=self.request.user.department
            )

        ctx['recent_movements'] = movements_qs[:5]

        # Alertas activas
        from alertas.models import Alert
        alerts_qs = Alert.objects.filter(is_read=False).select_related('product')
        if self.request.user.role != 'admin':
            alerts_qs = alerts_qs.filter(
                product__department=self.request.user.department
            )
        ctx['active_alerts'] = alerts_qs[:5]

        return ctx


class ProductListView(LoginRequiredMixin, DepartmentFilterMixin, ListView):
    """Lista de productos del inventario."""
    model = Product
    template_name = 'inventario/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('category', 'department')
        # Búsqueda
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
            
        # Filtro por departamento (solo admin)
        print("IS ADMIN:", getattr(self.request.user, 'is_admin', False))
        if self.request.user.is_admin:
            dept_id = self.request.GET.get('department')
            print("DEPT ID:", dept_id)
            if dept_id:
                qs = qs.filter(department_id=dept_id)
                print("QS AFTER FILTER:", qs.query)
                
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_admin:
            from usuarios.models import Department
            ctx['departments'] = Department.objects.filter(is_active=True)
            
            dept_param = self.request.GET.get('department')
            if dept_param and dept_param.isdigit():
                ctx['selected_dept'] = int(dept_param)
            else:
                ctx['selected_dept'] = None
                
        return ctx


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Crear producto."""
    model = Product
    form_class = ProductForm
    template_name = 'inventario/product_form.html'
    success_url = reverse_lazy('inventario:product_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.role != 'admin':
            form.instance.department = self.request.user.department
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, DepartmentFilterMixin, UpdateView):
    """Editar producto."""
    model = Product
    form_class = ProductForm
    template_name = 'inventario/product_form.html'
    success_url = reverse_lazy('inventario:product_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ProductDeleteView(LoginRequiredMixin, DepartmentFilterMixin, DeleteView):
    """Eliminar producto."""
    model = Product
    template_name = 'inventario/product_confirm_delete.html'
    success_url = reverse_lazy('inventario:product_list')
