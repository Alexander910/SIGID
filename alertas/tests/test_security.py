from django.test import TestCase
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
        self.encargado1 = User.objects.create_user(
            username='user_it',
            password='password123',
            role='encargado',
            department=self.dept1,
        )
        self.encargado2 = User.objects.create_user(
            username='user_hr',
            password='password123',
            role='encargado',
            department=self.dept2,
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin',
        )

        # Create Category and Products
        self.category = Category.objects.create(name='General')
        self.product_it = Product.objects.create(
            code='P01',
            name='Laptop IT',
            category=self.category,
            department=self.dept1,
            quantity=0,
            min_stock=5,
        )
        self.product_hr = Product.objects.create(
            code='P02',
            name='Desk HR',
            category=self.category,
            department=self.dept2,
            quantity=0,
            min_stock=5,
        )

        # Create Alerts
        self.alert_it = Alert.objects.create(
            product=self.product_it,
            alert_type='sin_stock',
            message='Sin stock de Laptop IT',
        )
        self.alert_hr = Alert.objects.create(
            product=self.product_hr,
            alert_type='sin_stock',
            message='Sin stock de Desk HR',
        )

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        """Verify that user_it gets 404 when attempting to mark HR alert as read (IDOR prevention)."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_hr.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_hr.refresh_from_db()
        self.assertFalse(self.alert_hr.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Verify that user_it can mark IT alert as read."""
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_it.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify that admin can mark any department alert as read."""
        self.client.login(username='admin', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_hr.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_hr.refresh_from_db()
        self.assertTrue(self.alert_hr.is_read)
