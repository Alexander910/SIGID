from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
        self.user1 = User.objects.create_user(
            username="user1",
            password="password123",
            role="encargado",
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="password123",
            role="encargado",
            department=self.dept2
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="password123",
            role="admin"
        )

        # Create Category
        self.cat = Category.objects.create(name="Cat 1")

        # Create Products
        self.prod1 = Product.objects.create(
            name="Prod 1",
            code="P1",
            category=self.cat,
            department=self.dept1,
            quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2",
            code="P2",
            category=self.cat,
            department=self.dept2,
            quantity=10
        )

        # Create Alerts
        self.alert1 = Alert.objects.create(
            product=self.prod1,
            alert_type="stock_bajo",
            message="Low stock dept 1"
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type="stock_bajo",
            message="Low stock dept 2"
        )

    def test_user_cannot_mark_other_dept_alert_as_read(self):
        """Verify that user1 cannot mark alert2 (Dept 2) as read."""
        self.client.login(username="user1", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_dept_alert_as_read(self):
        """Verify that user1 can mark alert1 (Dept 1) as read."""
        self.client.login(username="user1", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302) # Redirects to list
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify that admin can mark any alert as read."""
        self.client.login(username="admin", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
