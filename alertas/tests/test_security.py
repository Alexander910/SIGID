from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role="encargado")
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role="encargado")

        self.cat = Category.objects.create(name="Cat")

        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, category=self.cat)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

    def test_alert_mark_read_idor(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username="user1", password="password")

        # Try to mark alert2 (Dept 2) as read using user1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "user1 should NOT be able to mark alert2 as read!")

    def test_alert_mark_all_read_isolation(self):
        """Test that mark all read only affects alerts from the user's department."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_all_read')
        response = self.client.post(url)

        self.alert1.refresh_from_db()
        self.alert2.refresh_from_db()

        self.assertTrue(self.alert1.is_read, "User 1 should have marked their own alert as read")
        self.assertFalse(self.alert2.is_read, "User 1 should NOT have marked alert from Dept 2 as read")
