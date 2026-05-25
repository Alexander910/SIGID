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

        self.cat = Category.objects.create(name="Cat 1")
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, category=self.cat, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat, quantity=10)

        self.alert1 = Alert.objects.create(product=self.prod1, alert_type='stock_bajo', message="Low stock 1")
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type='stock_bajo', message="Low stock 2")

    def test_idor_mark_read(self):
        """Test that a user cannot mark as read an alert from another department."""
        self.client.login(username="user1", password="password")

        # User 1 tries to mark Alert 2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404 because User 1 doesn't have access to Alert 2
        # BUT currently it likely returns 302 (redirect) because it's vulnerable
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "Vulnerable to IDOR: User can mark read alerts from other departments")
        self.assertEqual(response.status_code, 404, "Vulnerable to IDOR: Should return 404 for alerts of other departments")
