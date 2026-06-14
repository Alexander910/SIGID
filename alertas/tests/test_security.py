from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(
            username="user1",
            password="password123",
            department=self.dept1,
            role='encargado'
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="password123",
            department=self.dept2,
            role='encargado'
        )

        self.product2 = Product.objects.create(
            name="Product 2",
            code="P2",
            department=self.dept2,
            quantity=10
        )

        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message="Low stock"
        )

        self.client = Client()

    def test_unauthorized_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        # It should probably return 404 or 403 if it was secure.
        # Currently it likely redirects and succeeds.
        self.alert2.refresh_from_db()

        # If the vulnerability exists, is_read will be True
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark User 2's alert as read")
