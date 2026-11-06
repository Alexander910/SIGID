from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    """Security tests to verify IDOR protection on AlertMarkReadView."""

    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Dept A', code='DPTA'
        )
        self.dept_b = Department.objects.create(
            name='Dept B', code='DPTB'
        )

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

        self.category = Category.objects.create(
            name='General'
        )
        self.product_b = Product.objects.create(
            name='Product B',
            code='PRD-B',
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Stock low for Product B',
            is_read=False
        )

        self.client = Client()

    def test_idor_cross_department_alert_mark_read_forbidden(self):
        """User from dept A cannot mark alert from dept B as read (404)."""
        self.client.login(username='user_a', password='password123')
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_authorized_department_alert_mark_read(self):
        """User from dept B can mark alert from dept B as read."""
        self.client.login(username='user_b', password='password123')
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin user can mark alert from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
