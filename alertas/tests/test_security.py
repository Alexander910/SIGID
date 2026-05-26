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

    def test_idor_mark_read_different_department(self):
        """
        Verify that a user from Dept 1 cannot mark an alert from Dept 2 as read.
        """
        self.client.login(username="user1", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # This should fail (e.g., 404) if secured, but currently it likely succeeds (302 redirect)
        response = self.client.post(url)

        self.alert2.refresh_from_db()

        # If vulnerable, this will be True
        # If secured, it should still be False because user1 shouldn't be able to change it
        # Actually, the view should return 404 if the object is not found in the user's scope

        if self.alert2.is_read:
            self.fail("VULNERABILITY: User from Dept 1 marked an alert from Dept 2 as read!")

        self.assertEqual(response.status_code, 404)
