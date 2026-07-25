from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    """Security tests to verify department isolation and prevent IDOR on AlertMarkReadView."""

    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Department A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Department B", code="DEPTB")

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
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin",
        )

        # Create products
        self.category = Category.objects.create(name="General")
        self.product_a = Product.objects.create(
            name="Product A",
            code="PA",
            category=self.category,
            department=self.dept_a,
            quantity=10,
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PB",
            category=self.category,
            department=self.dept_b,
            quantity=10,
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Stock bajo para Product A",
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Stock bajo para Product B",
            is_read=False,
        )

        self.client = Client()

    def test_encargado_can_mark_own_department_alert_read(self):
        """Verify that an encargado can mark an alert from their own department as read."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})
        response = self.client.post(url)

        # Should redirect to the alert list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("alertas:alert_list"))

        # Alert should be marked read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_encargado_cannot_mark_other_department_alert_read(self):
        """Verify that an encargado receives 404 when trying to mark other department's alert as read (preventing IDOR)."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        # Should be forbidden / not found (404 is secure as it doesn't leak existence of other department's alert)
        self.assertEqual(response.status_code, 404)

        # Alert should NOT be marked read
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_department_alert_read(self):
        """Verify that an admin user can mark any alert as read regardless of department."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        # Should redirect to the alert list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("alertas:alert_list"))

        # Alert should be marked read
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
