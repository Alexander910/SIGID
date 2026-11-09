from django.test import TestCase, Client
from django.urls import reverse

from alertas.models import Alert
from inventario.models import Category, Product
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    """Security tests to verify IDOR protection on alert management."""

    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Dept A',
            code='DPT-A',
        )
        self.dept_b = Department.objects.create(
            name='Dept B',
            code='DPT-B',
        )

        self.category = Category.objects.create(
            name='Test Category',
            description='Test Desc',
        )

        self.user_dept_a = User.objects.create_user(
            username='user_a',
            password='Password123!',
            role='encargado',
            department=self.dept_a,
        )
        self.user_dept_b = User.objects.create_user(
            username='user_b',
            password='Password123!',
            role='encargado',
            department=self.dept_b,
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='Password123!',
            role='admin',
            department=self.dept_a,
        )

        self.product_b = Product.objects.create(
            name='Product B',
            code='PRD-B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )
        self.alert_dept_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Product B out of stock',
            is_read=False,
        )

        self.client_a = Client()
        self.client_a.force_login(self.user_dept_a)

        self.client_b = Client()
        self.client_b.force_login(self.user_dept_b)

        self.admin_client = Client()
        self.admin_client.force_login(self.admin_user)

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """User from dept A should receive 404 when marking dept B alert."""
        url = reverse('alertas:alert_mark_read', args=[self.alert_dept_b.pk])
        response = self.client_a.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_dept_b.refresh_from_db()
        self.assertFalse(self.alert_dept_b.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """User from dept B can mark dept B alert as read."""
        url = reverse('alertas:alert_mark_read', args=[self.alert_dept_b.pk])
        response = self.client_b.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert_dept_b.refresh_from_db()
        self.assertTrue(self.alert_dept_b.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        """Admin can mark alerts across departments as read."""
        url = reverse('alertas:alert_mark_read', args=[self.alert_dept_b.pk])
        response = self.admin_client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert_dept_b.refresh_from_db()
        self.assertTrue(self.alert_dept_b.is_read)
