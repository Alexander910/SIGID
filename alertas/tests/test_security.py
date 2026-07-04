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

        self.product1 = Product.objects.create(name="Product 1", code="P1", department=self.dept1)
        self.product2 = Product.objects.create(name="Product 2", code="P2", department=self.dept2)

        self.alert1 = Alert.objects.create(product=self.product1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.product2, message="Alert 2")

        self.client1 = Client()
        self.client1.login(username="user1", password="password")

    def test_cannot_mark_other_department_alert_as_read(self):
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client1.post(url)

        # Should return 404 or at least not mark it as read
        # Current implementation will return 302 and mark it as read (VULNERABLE)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User should not be able to mark alert from another department as read")
        self.assertEqual(response.status_code, 404)
