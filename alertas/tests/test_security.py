from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_it = Department.objects.create(name='IT', code='IT', is_active=True)
        self.dept_hr = Department.objects.create(name='HR', code='HR', is_active=True)

        # Create category
        self.cat = Category.objects.create(name='Electronics')

        # Create users
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
            department=self.dept_it
        )
        self.user_it = User.objects.create_user(
            username='it_user',
            password='password123',
            role='encargado',
            department=self.dept_it
        )
        self.user_hr = User.objects.create_user(
            username='hr_user',
            password='password123',
            role='encargado',
            department=self.dept_hr
        )

        # Create products
        self.prod_it = Product.objects.create(
            name='IT Laptop',
            code='IT_LAPTOP',
            category=self.cat,
            department=self.dept_it,
            quantity=10,
            min_stock=5
        )
        self.prod_hr = Product.objects.create(
            name='HR Desk',
            code='HR_DESK',
            category=self.cat,
            department=self.dept_hr,
            quantity=8,
            min_stock=4
        )

        # Create alerts
        self.alert_it = Alert.objects.create(
            product=self.prod_it,
            alert_type='stock_bajo',
            message='IT stock bajo',
            is_read=False
        )
        self.alert_hr = Alert.objects.create(
            product=self.prod_hr,
            alert_type='stock_bajo',
            message='HR stock bajo',
            is_read=False
        )

        # Clients
        self.client_it = Client()
        self.client_it.login(username='it_user', password='password123')

        self.client_hr = Client()
        self.client_hr.login(username='hr_user', password='password123')

        self.client_admin = Client()
        self.client_admin.login(username='admin_user', password='password123')

    def test_own_department_alert_mark_read_success(self):
        """Non-admin user can mark alerts from their own department as read."""
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_it.pk})
        response = self.client_it.post(url)
        self.assertEqual(response.status_code, 302) # Redirect to alert list
        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_other_department_alert_mark_read_denied(self):
        """Non-admin user receives 404 and cannot mark alerts from other departments as read."""
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_hr.pk})
        response = self.client_it.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_hr.refresh_from_db()
        self.assertFalse(self.alert_hr.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Admin user can mark any department's alert as read."""
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_hr.pk})
        response = self.client_admin.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_hr.refresh_from_db()
        self.assertTrue(self.alert_hr.is_read)
