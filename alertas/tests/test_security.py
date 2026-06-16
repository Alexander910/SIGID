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
            username="user1", password="password", role="encargado", department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", role="encargado", department=self.dept2
        )

        self.product1 = Product.objects.create(
            name="Product 1", code="P1", department=self.dept1, quantity=10
        )
        self.product2 = Product.objects.create(
            name="Product 2", code="P2", department=self.dept2, quantity=10
        )

        self.alert1 = Alert.objects.create(product=self.product1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.product2, message="Alert 2")

    def test_user_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user1", password="password")

        # user1 attempts to mark alert2 (dept2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404 if we fix it correctly by filtering the queryset
        # or at least not mark it as read.
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark Alert 2 as read")
        self.assertEqual(response.status_code, 404)
