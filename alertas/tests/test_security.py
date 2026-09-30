from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='IT', code='IT01')
        self.dept2 = Department.objects.create(name='HR', code='HR01')

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )
        self.user_dept1 = User.objects.create_user(
            username='user_dept1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username='user_dept2',
            password='password123',
            role='encargado',
            department=self.dept2
        )

        # Create category and products
        self.category = Category.objects.create(name='General', description='General category')
        self.product1 = Product.objects.create(
            code='P001',
            name='Product Dept 1',
            category=self.category,
            department=self.dept1,
            quantity=2,
            min_stock=5
        )
        self.product2 = Product.objects.create(
            code='P002',
            name='Product Dept 2',
            category=self.category,
            department=self.dept2,
            quantity=1,
            min_stock=5
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product1,
            alert_type='stock_bajo',
            message='Stock bajo en Dept 1'
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message='Stock bajo en Dept 2'
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify that a non-admin user receives a 404 when trying to mark an alert from another department as read."""
        self.client.login(username='user_dept1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Verify that a non-admin user can mark an alert from their own department as read."""
        self.client.login(username='user_dept1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        """Verify that an admin user can mark an alert from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
