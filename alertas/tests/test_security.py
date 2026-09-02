from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        self.user_a = User.objects.create_user(
            username='user_a',
            email='usera@example.com',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            email='userb@example.com',
            password='password123',
            role='encargado',
            department=self.dept_b
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='password123',
            role='admin'
        )

        self.category = Category.objects.create(name='General')

        self.prod_a = Product.objects.create(
            code='P001',
            name='Prod A',
            category=self.category,
            department=self.dept_a,
            quantity=5,
            min_stock=10
        )
        self.prod_b = Product.objects.create(
            code='P002',
            name='Prod B',
            category=self.category,
            department=self.dept_b,
            quantity=5,
            min_stock=10
        )

        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='stock_bajo',
            message='Stock bajo en Prod A'
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='stock_bajo',
            message='Stock bajo en Prod B'
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """User A should get 404 when trying to mark User B's alert as read (IDOR prevention)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User A can mark their own department's alert as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin user can mark any department's alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
