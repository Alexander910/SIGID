from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Department A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Department B', code='DEPT_B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a,
        )
        self.user_admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        # Create category and products
        self.category = Category.objects.create(name='General', description='General category')
        self.product_a = Product.objects.create(
            name='Product A',
            code='PROD_A',
            department=self.dept_a,
            category=self.category,
            quantity=0,
            min_stock=5,
        )
        self.product_b = Product.objects.create(
            name='Product B',
            code='PROD_B',
            department=self.dept_b,
            category=self.category,
            quantity=0,
            min_stock=5,
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Stock zero for Product A',
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Stock zero for Product B',
            is_read=False,
        )

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        """User from Department A cannot mark Department B's alert as read (IDOR prevention)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verify alert_b remains unread in DB
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """User from Department A can mark Department A's alert as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify alert_a is marked as read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin can mark alerts from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify alert_b is marked as read
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
