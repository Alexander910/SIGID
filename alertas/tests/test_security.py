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
        self.user1 = User.objects.create_user(username="user1", password="password", role="encargado", department=self.dept1)
        self.user2 = User.objects.create_user(username="user2", password="password", role="encargado", department=self.dept2)

        # Create category
        self.cat = Category.objects.create(name="General")

        # Create products
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, alert_type="stock_bajo", message="Bajo stock 1")
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type="stock_bajo", message="Bajo stock 2")

    def test_user_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user1", password="password")

        # URL for marking alert2 (dept2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # This SHOULD fail or not mark it as read if we have proper security
        # Currently it uses get_object_or_404(Alert, pk=pk) which doesn't check department
        response = self.client.post(url)

        # Refresh from DB
        self.alert2.refresh_from_db()

        # If vulnerable, it will be True. If secure, it should still be False (or 404)
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark User 2's alert as read (IDOR)")
