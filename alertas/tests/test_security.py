from django.test import TestCase, Client
from django.urls import reverse

from alertas.models import Alert
from inventario.models import Product
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Departamento A',
            code='DEP-A',
        )
        self.dept_b = Department.objects.create(
            name='Departamento B',
            code='DEP-B',
        )

        self.user_a = User.objects.create_user(
            username='encargado_a',
            password='password123',
            role='encargado',
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username='encargado_b',
            password='password123',
            role='encargado',
            department=self.dept_b,
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.product_b = Product.objects.create(
            name='Producto B',
            code='PRD-B',
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Stock agotado en B',
            is_read=False,
        )

        self.client_a = Client()
        self.client_a.force_login(self.user_a)

        self.client_b = Client()
        self.client_b.force_login(self.user_b)

        self.client_admin = Client()
        self.client_admin.force_login(self.admin)

    def test_non_admin_cannot_mark_alert_from_other_department_as_read(self):
        # User A attempts to mark Alert B as read -> IDOR attempt
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client_a.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_non_admin_can_mark_own_department_alert_as_read(self):
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client_b.post(url)

        self.assertRedirects(response, reverse('alertas:alert_list'))
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client_admin.post(url)

        self.assertRedirects(response, reverse('alertas:alert_list'))
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
