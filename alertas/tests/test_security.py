from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Product, Category
from alertas.models import Alert

User = get_user_model()


class AlertSecurityTests(TestCase):
    """Pruebas de seguridad para evitar IDOR en alertas."""

    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name='Departamento A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Departamento B', code='DEPTB')

        # Crear usuarios (encargados)
        self.user_a = User.objects.create_user(
            username='encargado_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='encargado_b',
            password='password123',
            role='encargado',
            department=self.dept_b
        )

        # Crear administrador
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Crear categoría
        self.category = Category.objects.create(name='General')

        # Crear productos para cada departamento
        self.product_a = Product.objects.create(
            name='Producto A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name='Producto B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        # Crear alertas
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Producto A sin stock',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Producto B sin stock',
            is_read=False
        )

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """Verifica que un encargado no pueda marcar una alerta de otro departamento como leída (IDOR)."""
        self.client.login(username='encargado_a', password='password123')

        # Intentar marcar la alerta B (de Dept B) usando encargado A (de Dept A)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Debe retornar 404 (Not Found) debido al get_object_or_404 con queryset filtrado
        self.assertEqual(response.status_code, 404)

        # La alerta no debe haber sido marcada como leída
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_alert_as_read(self):
        """Verifica que un encargado pueda marcar una alerta de su propio departamento como leída."""
        self.client.login(username='encargado_a', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        # Redirecciona a la lista de alertas
        self.assertEqual(response.status_code, 302)

        # La alerta debe haberse marcado como leída
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verifica que un administrador pueda marcar cualquier alerta como leída."""
        self.client.login(username='admin_user', password='password123')

        # Admin marca la alerta de Dept B
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
