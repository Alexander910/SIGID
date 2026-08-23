from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            role='encargado',
            department=self.dept_b
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create products
        self.prod_a = Product.objects.create(
            name='Prod A', code='PA', department=self.dept_a
        )
        self.prod_b = Product.objects.create(
            name='Prod B', code='PB', department=self.dept_b
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a, alert_type='stock_bajo', message='Stock bajo A'
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b, alert_type='stock_bajo', message='Stock bajo B'
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify IDOR prevention: User A cannot mark Alert B (Dept B) as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User A can mark Alert A (Dept A) as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin user can mark any alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
