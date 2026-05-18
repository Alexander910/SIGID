from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role='encargado')

        self.cat = Category.objects.create(name="Cat")
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10)

        self.alert2 = Alert.objects.create(product=self.prod2, alert_type='stock_bajo', message="Low stock")

    def test_unauthorized_mark_read(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        # Should return 404 since we filter the queryset by user's department
        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_authorized_mark_read(self):
        """Test that a user can mark their own department alert as read."""
        alert1 = Alert.objects.create(
            product=Product.objects.create(name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10),
            alert_type='stock_bajo', message="Low stock"
        )
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': alert1.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        alert1.refresh_from_db()
        self.assertTrue(alert1.is_read)
