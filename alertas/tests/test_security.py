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
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Low stock P1", alert_type='stock_minimo')
        self.alert2 = Alert.objects.create(product=self.prod2, message="Low stock P2", alert_type='stock_minimo')

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user1", password="password")

        # user1 belongs to dept1, should not be able to mark alert2 (dept2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # If it's vulnerable, it will redirect (302) and mark as read
        # If it's secure, it should probably return 404

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "Encargado was able to mark an alert from another department as read!")
