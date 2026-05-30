from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role="encargado")
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role="encargado")

        self.cat = Category.objects.create(name="Cat")
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", category=self.cat, department=self.dept1)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

    def test_idor_mark_read_single(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark User 2's alert as read")
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_department_change_on_update(self):
        """Test that user1 cannot change a product's department to dept2 via UpdateView."""
        self.client.login(username="user1", password="password")
        url = reverse('inventario:product_update', kwargs={'pk': self.prod1.pk})

        # Data trying to change department to dept2
        data = {
            'name': 'Prod 1 Updated',
            'code': 'P1',
            'category': self.cat.pk,
            'department': self.dept2.pk,
            'quantity': 10,
            'min_stock': 5,
        }

        response = self.client.post(url, data)

        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.department, self.dept1, "User 1 should not be able to change product department")
