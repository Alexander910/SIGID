from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(
            username="user1",
            password="password123",
            role="encargado",
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="password123",
            role="encargado",
            department=self.dept2
        )

        self.cat = Category.objects.create(name="Cat 1")

        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10
        )

        self.alert1 = Alert.objects.create(
            product=self.prod1, message="Low stock P1", alert_type="stock_bajo"
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2, message="Low stock P2", alert_type="stock_bajo"
        )

    def test_user_cannot_mark_alert_from_another_department_as_read(self):
        self.client.login(username="user1", password="password123")

        # User 1 tries to mark Alert 2 (from Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Should be 404 if we filter correctly, or at least it shouldn't mark it as read
        # If it's vulnerable, it will return 302 (redirect) and mark it as read

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark User 2's alert as read")
        self.assertEqual(response.status_code, 404)
