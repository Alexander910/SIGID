from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Department A", code="DEPT_A")
        self.dept_b = Department.objects.create(name="Department B", code="DEPT_B")

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
            is_superuser=True,
        )

        # Create category and products
        self.category = Category.objects.create(name="General")
        self.product_a = Product.objects.create(
            name="Product A",
            code="PROD_A",
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5,
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PROD_B",
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="sin_stock",
            message="Product A is out of stock",
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="sin_stock",
            message="Product B is out of stock",
            is_read=False,
        )

        self.client = Client()

    def test_user_cannot_mark_other_department_alert_read(self):
        """User from Dept A should NOT be able to mark Dept B's alert as read (IDOR prevention)."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404)

        # Verify alert_b is still unread
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_read(self):
        """User from Dept A should be able to mark Dept A's alert as read."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert_a is marked as read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Admin user should be able to mark any department's alert as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert_b is marked as read
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
