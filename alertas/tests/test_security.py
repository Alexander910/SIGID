from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert


class AlertMarkReadSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Dept A", code="DEPT_A")
        self.dept_b = Department.objects.create(name="Dept B", code="DEPT_B")

        # Create users
        self.user_a = User.objects.create_user(
            username="user_a",
            password="password123",
            role="encargado",
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            password="password123",
            role="encargado",
            department=self.dept_b,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="password123",
            role="admin",
        )

        # Create products
        self.prod_a = Product.objects.create(
            name="Product A",
            code="CODE-A",
            department=self.dept_a,
            quantity=10,
            min_stock=5,
        )
        self.prod_b = Product.objects.create(
            name="Product B",
            code="CODE-B",
            department=self.dept_b,
            quantity=10,
            min_stock=5,
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type="stock_bajo",
            message="Alert A",
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type="stock_bajo",
            message="Alert B",
            is_read=False,
        )

        self.url_alert_a = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})

    def test_user_cannot_mark_read_alert_from_other_department(self):
        """User B should not be able to mark Alert A (Dept A) as read -> 404 expected."""
        self.client.login(username="user_b", password="password123")
        response = self.client.post(self.url_alert_a)
        self.assertEqual(response.status_code, 404)

        # Verify DB state remained unchanged
        self.alert_a.refresh_from_db()
        self.assertFalse(self.alert_a.is_read)

    def test_user_can_mark_read_alert_from_own_department(self):
        """User A should be able to mark Alert A (Dept A) as read."""
        self.client.login(username="user_a", password="password123")
        response = self.client.post(self.url_alert_a)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_read_alert_from_any_department(self):
        """Admin should be able to mark any alert as read."""
        self.client.login(username="admin", password="password123")
        response = self.client.post(self.url_alert_a)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)
