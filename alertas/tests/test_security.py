from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Create category
        self.category = Category.objects.create(name='General')

        # Create users
        self.user_dept1 = User.objects.create_user(
            username='user1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )

        # Create products
        self.product_dept1 = Product.objects.create(
            code='P1',
            name='Product 1',
            category=self.category,
            department=self.dept1,
            quantity=5,
            min_stock=10
        )
        self.product_dept2 = Product.objects.create(
            code='P2',
            name='Product 2',
            category=self.category,
            department=self.dept2,
            quantity=5,
            min_stock=10
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1,
            alert_type='stock_bajo',
            message='Stock bajo Dept 1'
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product_dept2,
            alert_type='stock_bajo',
            message='Stock bajo Dept 2'
        )

    def test_non_admin_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})

        response = self.client.post(url)

        # Non-admin from Dept 1 attempting to access Dept 2's alert should receive 404
        self.assertEqual(response.status_code, 404)

        # Verify alert status did not change in DB
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_non_admin_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
