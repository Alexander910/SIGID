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
        self.user1 = User.objects.create_user(
            username="user1", password="password", department=self.dept1, role="encargado"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", department=self.dept2, role="encargado"
        )

        # Create category
        self.cat = Category.objects.create(name="Cat")

        # Create products
        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10
        )

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

        self.client1 = Client()
        self.client1.login(username="user1", password="password")

    def test_idor_mark_alert_read(self):
        """Test that a user cannot mark an alert from another department as read."""
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # User 1 tries to mark Alert 2 (Dept 2) as read
        response = self.client1.post(url)

        # Should be 404 since it shouldn't be found in their "accessible" alerts
        # Currently it will be 302 (redirect) because it's not filtered
        self.assertEqual(response.status_code, 404)

        # Verify alert is still unread
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Test that an admin can mark an alert from any department as read."""
        admin = User.objects.create_user(
            username="admin_user", password="password", role="admin"
        )
        self.client.login(username="admin_user", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302) # Redirects on success
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
