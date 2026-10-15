from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
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
            department=self.dept1,
        )
        self.user_dept2 = User.objects.create_user(
            username='user_hr',
            password='password123',
            role='encargado',
            department=self.dept2,
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        # Create category & products
        self.category = Category.objects.create(name='Electronics')
        self.product_dept1 = Product.objects.create(
            name='IT Laptop',
            code='LAP01',
            category=self.category,
            department=self.dept1,
            quantity=0,
            min_stock=5,
        )
        self.product_dept2 = Product.objects.create(
            name='HR Desk',
            code='DSK01',
            category=self.category,
            department=self.dept2,
            quantity=0,
            min_stock=5,
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1,
            alert_type='sin_stock',
            message='IT Laptop sin stock',
            is_read=False,
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product_dept2,
            alert_type='sin_stock',
            message='HR Desk sin stock',
            is_read=False,
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """User from Dept 1 should get 404 when marking Dept 2 alert as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User from Dept 1 can mark Dept 1 alert as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin can mark alerts from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
