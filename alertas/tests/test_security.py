from django.test import TestCase, Client
from django.urls import reverse
from alertas.models import Alert
from inventario.models import Product
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    """Pruebas de seguridad para alertas (prevención de IDOR)."""

    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Departamento A',
            code='DEPT_A',
        )
        self.dept_b = Department.objects.create(
            name='Departamento B',
            code='DEPT_B',
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
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.prod_a = Product.objects.create(
            name='Producto A',
            code='PROD_A',
            department=self.dept_a,
            quantity=0,
            min_stock=5,
        )
        self.prod_b = Product.objects.create(
            name='Producto B',
            code='PROD_B',
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )

        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='sin_stock',
            message='Sin stock en Prod A',
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='sin_stock',
            message='Sin stock en Prod B',
            is_read=False,
        )

        self.client_a = Client()
        self.client_a.login(username='encargado_a', password='password123')

        self.client_admin = Client()
        self.client_admin.login(
            username='admin_user',
            password='password123',
        )

    def test_encargado_cannot_mark_other_dept_alert_as_read(self):
        """Verifica que un encargado no pueda marcar alertas de otro depto."""
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client_a.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_dept_alert_as_read(self):
        """Verifica que un encargado pueda marcar alertas de su depto."""
        url = reverse('alertas:alert_mark_read', args=[self.alert_a.pk])
        response = self.client_a.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verifica que un administrador pueda marcar cualquier alerta."""
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client_admin.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
