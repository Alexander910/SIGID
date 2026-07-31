from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Create users
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
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create category
        self.category = Category.objects.create(name='General')

        # Create products
        self.prod_a = Product.objects.create(
            name='Product A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.prod_b = Product.objects.create(
            name='Product B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='stock_bajo',
            message='Stock bajo de Product A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='stock_bajo',
            message='Stock bajo de Product B',
            is_read=False
        )

    def test_encargado_can_mark_own_alert_as_read(self):
        """Test that an encargado can mark an alert belonging to their own department as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_a.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_encargado_cannot_mark_other_alert_as_read(self):
        """Test that an encargado gets a 404 and database remains unchanged when trying to mark another department's alert as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  # Security expectation: 404 Not Found
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)  # Database state must remain unchanged

    def test_admin_can_mark_any_alert_as_read(self):
        """Test that an admin can mark any alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
