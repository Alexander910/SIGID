from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", role="encargado", department=self.dept1)
        self.user2 = User.objects.create_user(username="user2", password="password", role="encargado", department=self.dept2)

        self.cat = Category.objects.create(name="Cat 1")
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10, min_stock=5)

        self.alert2 = Alert.objects.create(product=self.prod2, alert_type="stock_bajo", message="Low stock")

    def test_idor_mark_read_other_department(self):
        """Test that a user cannot mark as read an alert from another department."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # user1 is in dept1, alert2 is in dept2. Should return 404.
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        # Verify alert is still unread
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)
