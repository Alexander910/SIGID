from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role='encargado')

        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

    def test_idor_alert_mark_read(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username="user1", password="password")

        # User 1 tries to mark Alert 2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404 or forbidden, but currently it likely returns 302 (success redirect)
        self.alert2.refresh_from_db()

        if response.status_code == 302 and self.alert2.is_read:
            print("\n[VULNERABILITY CONFIRMED] IDOR in AlertMarkReadView: User 1 marked Alert 2 as read.")
        elif response.status_code == 404:
            print("\n[SECURE] AlertMarkReadView is secure.")
        else:
            print(f"\n[UNKNOWN] Response status: {response.status_code}, Alert read: {self.alert2.is_read}")

        self.assertFalse(self.alert2.is_read, "User 1 should NOT be able to mark Alert 2 as read")
