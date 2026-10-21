from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a', password='password123', role='encargado', department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b', password='password123', role='encargado', department=self.dept_b
        )
        self.admin = User.objects.create_user(
            username='admin_user', password='password123', role='admin'
        )

        # Create category and products
        self.category = Category.objects.create(name='General', description='General category')
        self.product_a = Product.objects.create(
            name='Product A', code='PROD_A', category=self.category, department=self.dept_a, quantity=0
        )
        self.product_b = Product.objects.create(
            name='Product B', code='PROD_B', category=self.category, department=self.dept_b, quantity=0
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a, alert_type='sin_stock', message='Out of stock A', is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b, alert_type='sin_stock', message='Out of stock B', is_read=False
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify IDOR prevention: User A cannot mark Alert B as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User A can mark Alert A as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin user can mark Alert B as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
