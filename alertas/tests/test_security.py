from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role='encargado')

        # Create category
        self.cat = Category.objects.create(name="Cat 1")

        # Create products
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, category=self.cat, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat, quantity=10)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, message="Low stock P1", alert_type='stock_bajo')
        self.alert2 = Alert.objects.create(product=self.prod2, message="Low stock P2", alert_type='stock_bajo')

    def test_idor_alert_mark_read(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username="user1", password="password")

        # Try to mark alert2 (dept2) as read using user1 (dept1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Should be 404 if properly filtered
        self.assertEqual(response.status_code, 404)

        # Verify alert is still unread
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_authorized_alert_mark_read(self):
        """Test that a user can mark their own department's alert as read."""
        self.client.login(username="user1", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302) # Redirects to list
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
