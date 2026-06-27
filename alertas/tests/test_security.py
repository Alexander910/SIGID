from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.admin = User.objects.create_user(username="admin", password="password", role="admin")
        self.user1 = User.objects.create_user(username="user1", password="password", role="encargado", department=self.dept1)
        self.user2 = User.objects.create_user(username="user2", password="password", role="encargado", department=self.dept2)

        self.cat = Category.objects.create(name="Cat")
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, category=self.cat)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

    def test_idor_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # In a secure implementation, this should return 404 or at least not mark it as read
        # If it returns 302 (redirect) and the alert is read, it's a vulnerability
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 marked User 2's alert as read! IDOR detected.")
