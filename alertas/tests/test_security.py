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
            username="user1", password="password",
            department=self.dept1, role='encargado'
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password",
            department=self.dept2, role='encargado'
        )

        self.product1 = Product.objects.create(
            name="Product 1", code="P1", department=self.dept1, quantity=10
        )
        self.product2 = Product.objects.create(
            name="Product 2", code="P2", department=self.dept2, quantity=10
        )

        self.alert1 = Alert.objects.create(product=self.product1, message="Low stock P1")
        self.alert2 = Alert.objects.create(product=self.product2, message="Low stock P2")

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user1", password="password")

        # user1 (Dept 1) tries to mark alert2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # If it returns 404, it's secure. Currently it might return 302 (redirect) and mark it as read.
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User should not be able to mark other department's alert as read")
