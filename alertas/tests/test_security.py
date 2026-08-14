from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    """Security tests for Alert marking endpoint to prevent IDOR."""

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

        # Create category
        self.category = Category.objects.create(name="General")

        # Create products
        self.product_a = Product.objects.create(
            name="Product A",
            code="PRODA",
            category=self.category,
            department=self.dept_a,
            quantity=10,
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PRODB",
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

    def test_unauthorized_department_user_cannot_mark_alert_as_read(self):
        """Verify that a non-admin user cannot mark an alert from another department as read (IDOR prevention)."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)

        # Should return a 404 status code (get_object_or_404 filters by department)
        self.assertEqual(response.status_code, 404)

        # Check that the alert is still unread in the database
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_authorized_department_user_can_mark_alert_as_read(self):
        """Verify that a non-admin user can mark an alert from their own department as read."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})

        response = self.client.post(url)

        # Should redirect to alert list
        self.assertEqual(response.status_code, 302)

        # Check that the alert is marked as read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_user_can_mark_any_alert_as_read(self):
        """Verify that an admin user can mark any alert from any department as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)

        # Should redirect to alert list
        self.assertEqual(response.status_code, 302)

        # Check that the alert is marked as read
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
