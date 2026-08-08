from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Create category
        self.category = Category.objects.create(name='General Category')

        # Create products
        self.product_a = Product.objects.create(
            name='Product A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name='Product B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='stock_bajo',
            message='Stock bajo para Producto A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Stock bajo para Producto B',
            is_read=False
        )

        # Create users
        self.encargado_a = User.objects.create_user(
            username='encargado_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            password='password123',
            role='admin'
        )

        self.client = Client()

    def test_encargado_can_mark_own_department_alert_read(self):
        """Test that a non-admin user can mark an alert from their own department as read."""
        self.client.login(username='encargado_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirects to list
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_encargado_cannot_mark_other_department_alert_read_idor(self):
        """Test that a non-admin user gets 404 when trying to mark an alert from another department as read."""
        self.client.login(username='encargado_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  # Security restriction
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_department_alert_read(self):
        """Test that an admin can mark an alert from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
