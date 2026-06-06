from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role="encargado")
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role="encargado")

        self.product1 = Product.objects.create(name="Product 1", code="P1", department=self.dept1, quantity=10)
        self.product2 = Product.objects.create(name="Product 2", code="P2", department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.product1, message="Low stock P1")
        self.alert2 = Alert.objects.create(product=self.product2, message="Low stock P2")

        self.client = Client()

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """
        Verify that a user from Dept 1 cannot mark an alert from Dept 2 as read.
        """
        self.client.login(username="user1", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404
        self.assertEqual(response.status_code, 404)

        # Reload alert from DB
        self.alert2.refresh_from_db()

        # It should NOT be read
        self.assertFalse(self.alert2.is_read, "User 1 should not be able to mark alert 2 as read")

    def test_encargado_can_mark_own_alert_as_read(self):
        """
        Verify that a user from Dept 1 can mark their own alert as read.
        """
        self.client.login(username="user1", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)

        # It should redirect
        self.assertEqual(response.status_code, 302)

        # Reload alert from DB
        self.alert1.refresh_from_db()

        # It should be read
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """
        Verify that an admin can mark any alert as read.
        """
        admin = User.objects.create_superuser(username="admin", password="password", role="admin")
        self.client.login(username="admin", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should redirect
        self.assertEqual(response.status_code, 302)

        # Reload alert from DB
        self.alert2.refresh_from_db()

        # It should be read
        self.assertTrue(self.alert2.is_read)
