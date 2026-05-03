"""
Vistas de Reportes con filtros por fecha y exportación CSV.
"""
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View

from core.mixins import DepartmentFilterMixin
from core.utils import export_to_csv
from inventario.models import Product
from movimientos.models import Movement


class ReportView(LoginRequiredMixin, TemplateView):
    """Reporte de inventario y movimientos con filtros."""
    template_name = 'reportes/report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # ── Filtros de fecha ──
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        ctx['date_from'] = date_from
        ctx['date_to'] = date_to

        # ── Productos ──
        products = Product.objects.select_related('category', 'department')
        if user.role != 'admin':
            products = products.filter(department=user.department)
        ctx['products'] = products

        # ── Movimientos ──
        movements = Movement.objects.select_related(
            'product', 'user'
        ).order_by('-created_at')

        if user.role != 'admin':
            movements = movements.filter(
                product__department=user.department
            )

        if date_from:
            try:
                dt = datetime.strptime(date_from, '%Y-%m-%d')
                movements = movements.filter(created_at__date__gte=dt)
            except ValueError:
                pass

        if date_to:
            try:
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                movements = movements.filter(created_at__date__lte=dt)
            except ValueError:
                pass

        ctx['movements'] = movements[:100]

        # Estadísticas
        ctx['total_entries'] = movements.filter(type='entrada').count()
        ctx['total_exits'] = movements.filter(type='salida').count()

        return ctx


class ExportProductsCSVView(LoginRequiredMixin, View):
    """Exportar inventario a CSV."""

    def get(self, request):
        products = Product.objects.select_related('category', 'department')
        if request.user.role != 'admin':
            products = products.filter(department=request.user.department)

        fields = [
            ('code', 'Código'),
            ('name', 'Nombre'),
            ('category__name', 'Categoría'),
            ('department__name', 'Departamento'),
            ('quantity', 'Cantidad'),
            ('min_stock', 'Stock Mínimo'),
        ]

        return export_to_csv(products, 'inventario_sigid', fields)


class ExportMovementsCSVView(LoginRequiredMixin, View):
    """Exportar movimientos a CSV."""

    def get(self, request):
        movements = Movement.objects.select_related(
            'product', 'user'
        ).order_by('-created_at')

        if request.user.role != 'admin':
            movements = movements.filter(
                product__department=request.user.department
            )

        # Filtros de fecha
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        if date_from:
            try:
                dt = datetime.strptime(date_from, '%Y-%m-%d')
                movements = movements.filter(created_at__date__gte=dt)
            except ValueError:
                pass

        if date_to:
            try:
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                movements = movements.filter(created_at__date__lte=dt)
            except ValueError:
                pass

        fields = [
            ('product__name', 'Producto'),
            ('product__code', 'Código'),
            ('get_type_display', 'Tipo'),
            ('quantity', 'Cantidad'),
            ('user__username', 'Responsable'),
            ('observation', 'Observación'),
            ('created_at', 'Fecha'),
        ]

        return export_to_csv(movements, 'movimientos_sigid', fields)
