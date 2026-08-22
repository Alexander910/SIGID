from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    """Test IDOR protection for marking alerts as read."""

    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a,
        )

        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.cat = Category.objects.create(name='General')

        self.product_b = Product.objects.create(
            name='Product B',
            code='PROD_B',
            category=self.cat,
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )

        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Sin stock',
            is_read=False,
        )

    def test_non_admin_cannot_mark_other_department_alert_read(self):
        """User from Dept A cannot mark an alert from Dept B as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_non_admin_can_mark_own_department_alert_read(self):
        """User from Dept A can mark an alert from Dept A as read."""
        product_a = Product.objects.create(
            name='Product A',
            code='PROD_A',
            category=self.cat,
            department=self.dept_a,
            quantity=0,
            min_stock=5,
        )
        alert_a = Alert.objects.create(
            product=product_a,
            alert_type='sin_stock',
            message='Sin stock',
            is_read=False,
        )

        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        alert_a.refresh_from_db()
        self.assertTrue(alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Admin user can mark any alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
