from django.test import TestCase, Client
from django.urls import reverse

from alertas.models import Alert
from inventario.models import Category, Product
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    """Pruebas de seguridad e IDOR para el módulo de alertas."""

    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Departamento A',
            code='DEP-A',
        )
        self.dept_b = Department.objects.create(
            name='Departamento B',
            code='DEP-B',
        )

        self.user_a = User.objects.create_user(
            username='encargado_a',
            password='password123',
            role='encargado',
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username='encargado_b',
            password='password123',
            role='encargado',
            department=self.dept_b,
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.category = Category.objects.create(name='General')

        self.product_b = Product.objects.create(
            name='Producto B',
            code='PROD-B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Sin stock en Producto B',
            is_read=False,
        )

        self.client_a = Client()
        self.client_a.login(username='encargado_a', password='password123')

        self.client_b = Client()
        self.client_b.login(username='encargado_b', password='password123')

        self.client_admin = Client()
        self.client_admin.login(username='admin_user', password='password123')

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        """Un encargado no debe poder marcar alertas de otro departamento."""
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client_a.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Un encargado puede marcar alertas de su propio departamento."""
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client_b.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Un administrador puede marcar cualquier alerta como leída."""
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client_admin.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
