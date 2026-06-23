from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role='encargado')

        # Create products
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, quantity=10, min_stock=5)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, quantity=10, min_stock=5)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, alert_type='stock_bajo', message="Low stock P1")
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type='stock_bajo', message="Low stock P2")

    def test_idor_alert_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password")

        # Try to mark alert2 (Dept 2) as read using user1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # In a secure system, this should probably return 404
        # Currently it likely redirects (302) and succeeds

        self.alert2.refresh_from_db()

        # If vulnerable, this will fail (it will be True)
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark Alert 2 as read")
        self.assertEqual(response.status_code, 404, "Should return 404 for unauthorized alert access")
