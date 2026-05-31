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
            username="user1", password="password123", role="encargado", department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password123", role="encargado", department=self.dept2
        )

        self.cat = Category.objects.create(name="Cat 1")
        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10
        )

        self.alert1 = Alert.objects.create(product=self.prod1, message="Low stock 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Low stock 2")

    def test_idor_mark_read(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username="user1", password="password123")

        # Try to mark alert2 (Dept 2) as read using user1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Currently it returns 302 (redirect) and succeeds. It should ideally be 404.
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User should not be able to mark another department's alert as read")

    def test_unauthorized_department_modification(self):
        """Test that a user cannot change a product's department to one they don't belong to."""
        self.client.login(username="user1", password="password123")

        url = reverse('inventario:product_update', kwargs={'pk': self.prod1.pk})
        data = {
            'name': 'Updated Prod 1',
            'code': 'P1',
            'category': self.cat.pk,
            'department': self.dept2.pk, # Tampered: trying to move it to Dept 2
            'quantity': 10,
            'min_stock': 5,
        }
        response = self.client.post(url, data)

        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.department, self.dept1, "User should not be able to change product department")
