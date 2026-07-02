from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertasSecurityTests(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role="encargado")
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role="encargado")

        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

    def test_alert_mark_read_idor(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # This should fail (404) if secured, but currently it likely returns 302 and succeeds
        response = self.client.post(url)

        # If it returns 404, the fix is working. If it returns 302, it's vulnerable.
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark User 2's alert as read")
        self.assertEqual(response.status_code, 404)
