from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
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
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create category and products
        self.category = Category.objects.create(name='General', description='Desc')
        self.product_a = Product.objects.create(
            code='P001',
            name='Product A',
            category=self.category,
            department=self.dept_a,
            quantity=5,
            min_stock=10
        )
        self.product_b = Product.objects.create(
            code='P002',
            name='Product B',
            category=self.category,
            department=self.dept_b,
            quantity=2,
            min_stock=10
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='stock_bajo',
            message='Low stock A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Low stock B',
            is_read=False
        )

    def test_idor_prevented_for_other_department_alert(self):
        """Verify non-admin user cannot mark an alert from another department as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404)

        # Verify alert B remains unread in database
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_own_department_alert_mark_read(self):
        """Verify non-admin user can mark an alert from their own department as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Verify admin user can mark any alert from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
