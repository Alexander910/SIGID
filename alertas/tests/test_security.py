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
            username="user1", password="password", role="encargado", department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", role="encargado", department=self.dept2
        )

        self.cat = Category.objects.create(name="Cat")

        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10
        )

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user1", password="password")

        # User 1 belongs to Dept 1. Alert 2 belongs to Dept 2.
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        # It should probably return 404 if they don't have access to it
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)
