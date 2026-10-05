from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        self.user_a = User.objects.create_user(
            username='encargado_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='encargado_b',
            password='password123',
            role='encargado',
            department=self.dept_b
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        self.category = Category.objects.create(name='General')

        self.product_b = Product.objects.create(
            name='Product B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Stock cero',
            is_read=False
        )

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username='encargado_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # User A from Dept A attempting to mark Dept B alert as read should receive 404
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        product_a = Product.objects.create(
            name='Product A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        alert_a = Alert.objects.create(
            product=product_a,
            alert_type='sin_stock',
            message='Stock cero',
            is_read=False
        )

        self.client.login(username='encargado_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        alert_a.refresh_from_db()
        self.assertTrue(alert_a.is_read)
