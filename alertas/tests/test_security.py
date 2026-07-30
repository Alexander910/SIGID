from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create Departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Create Users
        self.encargado1 = User.objects.create_user(
            username='encargado1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.encargado2 = User.objects.create_user(
            username='encargado2',
            password='password123',
            role='encargado',
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create Category
        self.category = Category.objects.create(name='General')

        # Create Products
        self.product1 = Product.objects.create(
            name='Product 1',
            code='P1',
            category=self.category,
            department=self.dept1,
            quantity=10,
            min_stock=5
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            code='P2',
            category=self.category,
            department=self.dept2,
            quantity=10,
            min_stock=5
        )

        # Create Alerts
        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type='stock_bajo',
            message='Stock bajo para P1',
            is_read=False
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message='Stock bajo para P2',
            is_read=False
        )

    def test_encargado_cannot_mark_alert_from_other_department(self):
        """Verify that an encargado cannot mark as read an alert belonging to a different department (IDOR)."""
        self.client.login(username='encargado1', password='password123')

        # Try to mark alert2 (Dept 2) as read using encargado1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Verify it returns a 404 (Not Found) or similar restriction
        self.assertEqual(response.status_code, 404)

        # Reload alert2 from DB and check that is_read remains False
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_encargado_can_mark_own_alert(self):
        """Verify that an encargado can successfully mark as read an alert belonging to their own department."""
        self.client.login(username='encargado1', password='password123')

        # Mark alert1 (Dept 1) as read using encargado1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)

        # It should redirect to alert_list
        self.assertEqual(response.status_code, 302)

        # Reload from DB and verify it is indeed True
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert(self):
        """Verify that an administrator can mark any alert as read regardless of department."""
        self.client.login(username='admin_user', password='password123')

        # Admin marks alert1 as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
