from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Category, Product
from alertas.models import Alert

User = get_user_model()


class AlertSecurityTests(TestCase):
    """
    Security tests for the alerts system to prevent IDOR vulnerabilities.
    """

    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123',
            role='admin'
        )
        self.encargado_a = User.objects.create_user(
            username='encargado_a',
            email='a@example.com',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.encargado_b = User.objects.create_user(
            username='encargado_b',
            email='b@example.com',
            password='password123',
            role='encargado',
            department=self.dept_b
        )

        # Create category
        self.category = Category.objects.create(name='General')

        # Create products
        self.product_a = Product.objects.create(
            name='Product A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name='Product B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Product A is out of stock',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Product B is out of stock',
            is_read=False
        )

    def test_admin_can_mark_any_alert_read(self):
        """An admin user can mark any alert as read."""
        self.client.login(username='admin', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_authorized_user_can_mark_own_department_alert_read(self):
        """A department manager can mark an alert for their own department as read."""
        self.client.login(username='encargado_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_unauthorized_user_cannot_mark_other_department_alert_read(self):
        """
        An IDOR check: A department manager cannot mark an alert for another
        department as read and receives a 404 status.
        """
        self.client.login(username='encargado_b', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        # Should return 404 since they do not have access to this alert's department
        self.assertEqual(response.status_code, 404)

        # Verify database state remains unmodified
        self.alert_a.refresh_from_db()
        self.assertFalse(self.alert_a.is_read)
