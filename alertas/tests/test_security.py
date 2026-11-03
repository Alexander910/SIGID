from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertMarkReadSecurityTest(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(
            name='Dept A',
            code='DEPT_A'
        )
        self.dept_b = Department.objects.create(
            name='Dept B',
            code='DEPT_B'
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
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        self.cat = Category.objects.create(
            name='Test Category',
            description='Test Desc'
        )

        self.product_a = Product.objects.create(
            code='P001',
            name='Product A',
            category=self.cat,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            code='P002',
            name='Product B',
            category=self.cat,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Stock zero for Product A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Stock zero for Product B',
            is_read=False
        )

        self.client = Client()

    def test_user_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_a.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
