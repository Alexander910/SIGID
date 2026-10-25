from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='IT', code='IT01')
        self.dept2 = Department.objects.create(name='HR', code='HR01')

        # Create users
        self.user_dept1 = User.objects.create_user(
            username='user1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username='user2',
            password='password123',
            role='encargado',
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='password123',
            role='admin'
        )

        # Create category
        self.category = Category.objects.create(name='Electronics', description='Tech gear')

        # Create products
        self.product_dept1 = Product.objects.create(
            name='Laptop',
            code='LAP01',
            category=self.category,
            department=self.dept1,
            quantity=0,
            min_stock=5
        )
        self.product_dept2 = Product.objects.create(
            name='Printer',
            code='PRN01',
            category=self.category,
            department=self.dept2,
            quantity=0,
            min_stock=5
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1,
            alert_type='sin_stock',
            message='Laptop out of stock',
            is_read=False
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product_dept2,
            alert_type='sin_stock',
            message='Printer out of stock',
            is_read=False
        )

        self.client = Client()

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify non-admin user receives 404 when marking alert from another department."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        # Verify alert remains unread
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Verify non-admin user can mark alert from their own department as read."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert is marked as read
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify admin user can mark alerts from any department as read."""
        self.client.login(username='adminuser', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert is marked as read
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
