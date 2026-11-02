from django.test import TestCase, Client
from django.urls import reverse
from alertas.models import Alert
from inventario.models import Product, Category
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Dept A',
            code='DEPTA'
        )
        self.dept_b = Department.objects.create(
            name='Dept B',
            code='DEPTB'
        )

        self.category = Category.objects.create(
            name='Test Cat',
            description='Test Category'
        )

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

        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Sin stock dept B',
            is_read=False
        )
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Sin stock dept A',
            is_read=False
        )

        self.client_a = Client()
        self.client_a.login(username='user_a', password='password123')

        self.client_admin = Client()
        self.client_admin.login(
            username='admin_user',
            password='password123'
        )

    def test_encargado_cannot_mark_other_department_alert_read(self):
        url = reverse(
            'alertas:alert_mark_read',
            kwargs={'pk': self.alert_b.pk}
        )
        response = self.client_a.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_read(self):
        url = reverse(
            'alertas:alert_mark_read',
            kwargs={'pk': self.alert_a.pk}
        )
        response = self.client_a.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        url = reverse(
            'alertas:alert_mark_read',
            kwargs={'pk': self.alert_b.pk}
        )
        response = self.client_admin.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
