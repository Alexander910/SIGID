from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        self.user_encargado_a = User.objects.create_user(
            username='user_a',
            email='a@example.com',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_encargado_b = User.objects.create_user(
            username='user_b',
            email='b@example.com',
            password='password123',
            role='encargado',
            department=self.dept_b
        )
        self.user_admin = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='password123',
            role='admin'
        )

        self.category = Category.objects.create(name='General', description='General category')

        self.prod_a = Product.objects.create(
            code='PROD_A',
            name='Product A',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        self.prod_b = Product.objects.create(
            code='PROD_B',
            name='Product B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='sin_stock',
            message='Stock 0'
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='sin_stock',
            message='Stock 0'
        )

        self.client = Client()

    def test_encargado_cannot_mark_other_department_alert_read(self):
        """User A should receive 404 when trying to mark Alert B as read (IDOR prevention)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_read(self):
        """User A should successfully mark Alert A as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Admin user should successfully mark Alert B as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
