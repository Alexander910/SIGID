from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role='encargado')
        self.admin = User.objects.create_user(username="admin", password="password", role='admin')

        # Create category
        self.cat = Category.objects.create(name="Cat")

        # Create products
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10, min_stock=5)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10, min_stock=5)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, alert_type='stock_bajo', message="Low stock P1")
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type='stock_bajo', message="Low stock P2")

    def test_idor_alert_mark_read(self):
        """Test that a user cannot mark as read an alert from another department."""
        self.client.login(username="user1", password="password")

        # Try to mark alert2 (Dept 2) as read using user1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404 if fixed, but currently it likely returns 302 (redirect)
        # because it doesn't check department.

        self.alert2.refresh_from_db()
        self.assertEqual(response.status_code, 404, "Should return 404 for unauthorized alert access")
        self.assertFalse(self.alert2.is_read)
