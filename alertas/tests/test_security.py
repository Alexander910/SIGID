from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertIDORTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", role="encargado", department=self.dept1)
        self.user2 = User.objects.create_user(username="user2", password="password", role="encargado", department=self.dept2)

        self.cat = Category.objects.create(name="Cat")
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, category=self.cat, quantity=10)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat, quantity=10)

        self.alert1 = Alert.objects.create(product=self.prod1, alert_type="stock_bajo", message="Low stock 1")
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type="stock_bajo", message="Low stock 2")

        self.client1 = Client()
        self.client1.login(username="user1", password="password")

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        """
        Verify that a user from dept1 cannot mark an alert from dept2 as read.
        """
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client1.post(url)

        # Should ideally be 404 if we filter the queryset
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """
        Verify that a user from dept1 can mark an alert from dept1 as read.
        """
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client1.post(url)

        self.assertEqual(response.status_code, 302) # Redirects to list
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
