from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

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
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=0,
        )

        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Product B is out of stock',
            is_read=False,
        )

        self.client = Client()

    def test_idor_user_cannot_mark_other_department_alert_as_read(self):
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
