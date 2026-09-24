from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='IT', code='IT01')
        self.dept2 = Department.objects.create(name='HR', code='HR01')

        # Create users
        self.user_dept1 = User.objects.create_user(
            username='user_it',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username='user_hr',
            password='password123',
            role='encargado',
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create category & products
        self.category = Category.objects.create(name='General')
        self.prod_dept1 = Product.objects.create(
            name='Laptop', code='L01', category=self.category, department=self.dept1
        )
        self.prod_dept2 = Product.objects.create(
            name='Desk', code='D01', category=self.category, department=self.dept2
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.prod_dept1, alert_type='stock_bajo', message='Low stock'
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.prod_dept2, alert_type='stock_bajo', message='Low stock'
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify non-admin user gets 404 when marking alert of another department as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Confirm alert status is unchanged
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Verify non-admin user can mark alert of their own department as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify admin user can mark any department alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
