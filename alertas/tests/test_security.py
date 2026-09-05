from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert


class AlertMarkReadSecurityTests(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        # Crear usuarios
        self.user_a = User.objects.create_user(
            username='user_a',
            email='user_a@test.com',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='password123',
            role='admin'
        )

        # Crear productos y alertas
        self.product_a = Product.objects.create(
            code='PROD_A',
            name='Product A',
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            code='PROD_B',
            name='Product B',
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='stock_bajo',
            message='Stock bajo A'
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Stock bajo B'
        )

    def test_user_cannot_mark_alert_read_other_department(self):
        """Verifica que un usuario no admin no pueda marcar leída una alerta de otro departamento (IDOR)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_alert_read_own_department(self):
        """Verifica que un usuario pueda marcar leída una alerta de su propio departamento."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Verifica que un usuario admin pueda marcar leída cualquier alerta."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
