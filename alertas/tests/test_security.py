from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Product
from alertas.models import Alert

User = get_user_model()


class AlertMarkReadSecurityTests(TestCase):
    """
    Security tests for AlertMarkReadView to prevent IDOR (Insecure Direct Object Reference)
    vulnerabilities. Ensures non-admin users cannot read/modify alerts from other departments.
    """

    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Dept A", code="A")
        self.dept_b = Department.objects.create(name="Dept B", code="B")

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
            username="admin_user",
            password="password123",
            role="admin",
        )

        # Create products
        self.product_a = Product.objects.create(
            name="Product A",
            code="PA",
            department=self.dept_a,
            quantity=10,
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PB",
            department=self.dept_b,
            quantity=10,
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Alert A message",
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Alert B message",
            is_read=False,
        )

    def test_user_can_mark_own_department_alert_as_read(self):
        """
        A non-admin user should successfully mark an alert as read
        if it belongs to their department.
        """
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify database state was updated
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """
        A non-admin user must NOT be able to mark an alert from another
        department as read. It should return 404, and database state must be unchanged.
        """
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  # Security rule: 404 Not Found

        # Verify database state remains unchanged
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """
        An admin user should have full access to mark any alert from any
        department as read.
        """
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify database state was updated
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
