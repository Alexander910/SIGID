from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Depto 1", code="D1")
        self.dept2 = Department.objects.create(name="Depto 2", code="D2")

        # Create users
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password",
            role="admin"
        )
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            role="encargado",
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="password",
            role="encargado",
            department=self.dept2
        )

        # Create products
        self.prod1 = Product.objects.create(
            name="Product 1",
            code="P1",
            department=self.dept1,
            quantity=10,
            min_stock=5
        )
        self.prod2 = Product.objects.create(
            name="Product 2",
            code="P2",
            department=self.dept2,
            quantity=10,
            min_stock=5
        )

        # Create alerts
        self.alert1 = Alert.objects.create(
            product=self.prod1,
            alert_type="stock_bajo",
            message="Stock bajo prod 1",
            is_read=False
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type="stock_bajo",
            message="Stock bajo prod 2",
            is_read=False
        )

        self.client = Client()

    def test_non_admin_cannot_mark_other_dept_alert_read(self):
        # Login user1 (dept1)
        self.client.force_login(self.user1)

        # Try to mark alert2 (dept2) as read
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert2.pk})
        response = self.client.post(url)

        # Should return 404
        self.assertEqual(response.status_code, 404)

        # Alert should still be unread in DB
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_non_admin_can_mark_own_dept_alert_read(self):
        # Login user1 (dept1)
        self.client.force_login(self.user1)

        # Mark alert1 (dept1) as read
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert1.pk})
        response = self.client.post(url)

        # Should redirect to list view
        self.assertRedirects(response, reverse("alertas:alert_list"))

        # Alert should be marked read in DB
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_read(self):
        # Login admin
        self.client.force_login(self.admin)

        # Mark alert2 (dept2) as read
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert2.pk})
        response = self.client.post(url)

        # Should redirect to list view
        self.assertRedirects(response, reverse("alertas:alert_list"))

        # Alert should be marked read in DB
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
