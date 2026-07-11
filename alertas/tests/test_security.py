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
            name="Prod 1",
            code="P1",
            category=self.cat,
            department=self.dept1,
            quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2",
            code="P2",
            category=self.cat,
            department=self.dept2,
            quantity=10
        )

        self.alert1 = Alert.objects.create(
            product=self.prod1,
            alert_type="stock_bajo",
            message="Low stock"
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type="stock_bajo",
            message="Low stock"
        )

    def test_idor_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password123")

        # Attempt to mark alert2 (from dept2) as read using user1 (from dept1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404 (Not Found) because of the department filter in get_object_or_404
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 was able to mark User 2's alert as read! (IDOR)")
