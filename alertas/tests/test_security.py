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

        self.cat = Category.objects.create(name="Cat 1")
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat)

        self.alert2 = Alert.objects.create(product=self.prod2, message="Low stock", alert_type="stock_bajo")

    def test_idor_mark_read_other_department(self):
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # User 1 tries to mark User 2's alert as read
        response = self.client.post(url)

        # It should return 404 if we fix it
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User should not be able to mark another department's alert as read")
