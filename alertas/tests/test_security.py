from django.test import TestCase
from django.urls import reverse
from alertas.models import Alert
from inventario.models import Category, Product
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DPTB')

        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            role='encargado',
            department=self.dept_b,
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.category = Category.objects.create(name='General')

        self.product_b = Product.objects.create(
            name='Product B',
            code='PRD-B',
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5,
        )

        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Stock bajo en Product B',
            is_read=False,
        )

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        self.client.login(username='user_a', password='password123')
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin_user', password='password123')
        url = reverse(
            'alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
