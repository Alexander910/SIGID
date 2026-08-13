from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Product, Category
from alertas.models import Alert

User = get_user_model()

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_it = Department.objects.create(name='IT', code='IT', is_active=True)
        self.dept_hr = Department.objects.create(name='HR', code='HR', is_active=True)

        # Create users
        self.user_it = User.objects.create_user(
            username='user_it',
            email='it@example.com',
            password='password123',
            role='encargado',
            department=self.dept_it
        )
        self.user_hr = User.objects.create_user(
            username='user_hr',
            email='hr@example.com',
            password='password123',
            role='encargado',
            department=self.dept_hr
        )
        self.admin = User.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='password123',
            role='admin'
        )

        # Create products
        self.category = Category.objects.create(name='General')
        self.product_it = Product.objects.create(
            name='IT Laptop',
            code='LAP-IT',
            category=self.category,
            department=self.dept_it,
            quantity=10,
            min_stock=5
        )
        self.product_hr = Product.objects.create(
            name='HR Desk',
            code='DSK-HR',
            category=self.category,
            department=self.dept_hr,
            quantity=8,
            min_stock=4
        )

        # Create alerts
        self.alert_it = Alert.objects.create(
            product=self.product_it,
            alert_type='stock_bajo',
            message='IT stock bajo',
            is_read=False
        )
        self.alert_hr = Alert.objects.create(
            product=self.product_hr,
            alert_type='stock_bajo',
            message='HR stock bajo',
            is_read=False
        )

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_it.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_it.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_user_cannot_mark_other_department_alert_as_read_idor(self):
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_hr.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_hr.refresh_from_db()
        self.assertFalse(self.alert_hr.is_read)
