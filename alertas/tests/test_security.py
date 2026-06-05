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

        self.product1 = Product.objects.create(
            name="Product 1",
            code="P1",
            department=self.dept1,
            quantity=10
        )
        self.product2 = Product.objects.create(
            name="Product 2",
            code="P2",
            department=self.dept2,
            quantity=10
        )

        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type='stock_bajo',
            message="Bajo stock p1"
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message="Bajo stock p2"
        )

        self.client = Client()

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user1", password="password123")

        # user1 belongs to dept1, alert2 belongs to product2 in dept2
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Re-fetch alert2
        self.alert2.refresh_from_db()

        self.assertFalse(self.alert2.is_read, "User should not be able to mark other department's alert as read")
        self.assertEqual(response.status_code, 404, "Should return 404 for alert not in user's department")
