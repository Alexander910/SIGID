from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertMarkReadSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='IT', code='IT01')
        self.dept2 = Department.objects.create(name='HR', code='HR01')

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password123',
            role='admin'
        )
        self.user_dept1 = User.objects.create_user(
            username='user_it',
            email='it@test.com',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username='user_hr',
            email='hr@test.com',
            password='password123',
            role='encargado',
            department=self.dept2
        )

        # Create Category & Products
        self.category = Category.objects.create(name='General')
        self.product_dept1 = Product.objects.create(
            name='IT Laptop',
            code='LAP01',
            category=self.category,
            department=self.dept1,
            quantity=0,
            min_stock=5
        )
        self.product_dept2 = Product.objects.create(
            name='HR Chair',
            code='CHR01',
            category=self.category,
            department=self.dept2,
            quantity=0,
            min_stock=5
        )

        # Create Alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1,
            alert_type='sin_stock',
            message='Out of stock in IT',
            is_read=False
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product_dept2,
            alert_type='sin_stock',
            message='Out of stock in HR',
            is_read=False
        )

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        """Verify IDOR prevention: non-admin user cannot mark alert of another department as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        # Expect 404 Not Found due to queryset department filtering
        self.assertEqual(response.status_code, 404)

        # Verify state in database was unchanged
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Verify user can mark alert in their own department as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify admin user can mark any department alert as read."""
        self.client.login(username='admin', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
