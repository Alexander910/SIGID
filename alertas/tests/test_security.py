
from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class SecurityIDORTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password123", department=self.dept1, role="encargado")
        self.user2 = User.objects.create_user(username="user2", password="password123", department=self.dept2, role="encargado")

        self.category = Category.objects.create(name="Cat 1")

        self.product1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.category, department=self.dept1, quantity=10
        )
        self.product2 = Product.objects.create(
            name="Prod 2", code="P2", category=self.category, department=self.dept2, quantity=10
        )

        self.alert1 = Alert.objects.create(product=self.product1, message="Alert 1", alert_type="stock_bajo")
        self.alert2 = Alert.objects.create(product=self.product2, message="Alert 2", alert_type="stock_bajo")

    def test_idor_alert_mark_read(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username="user1", password="password123")

        # Try to mark alert2 (Dept 2) as read while being in Dept 1
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Refresh from DB
        self.alert2.refresh_from_db()

        # Expected: 404 Not Found (if IDOR is prevented by queryset filtering)
        self.assertEqual(response.status_code, 404, f"VULNERABILITY: User can access alerts from other departments! Response code: {response.status_code}")
        self.assertFalse(self.alert2.is_read)
