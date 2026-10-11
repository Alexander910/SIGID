from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create Category
        self.category = Category.objects.create(name="General", description="General Category")

        # Create Users
        self.user_dept1 = User.objects.create_user(
            username="user_dept1",
            password="password123",
            role="encargado",
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username="user_dept2",
            password="password123",
            role="encargado",
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin"
        )

        # Create Products
        self.product_dept1 = Product.objects.create(
            name="Prod 1",
            code="P1",
            category=self.category,
            department=self.dept1,
            quantity=2,
            min_stock=5
        )
        self.product_dept2 = Product.objects.create(
            name="Prod 2",
            code="P2",
            category=self.category,
            department=self.dept2,
            quantity=1,
            min_stock=5
        )

        # Create Alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1,
            alert_type="stock_bajo",
            message="Low stock on Prod 1",
            is_read=False
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product_dept2,
            alert_type="stock_bajo",
            message="Low stock on Prod 2",
            is_read=False
        )

    def test_non_admin_cannot_mark_other_department_alert_as_read(self):
        """User from Dept 1 should get 404 when marking an alert from Dept 2 as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        # Verify alert in Dept 2 is still unread
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_non_admin_can_mark_own_department_alert_as_read(self):
        """User from Dept 1 should be able to mark an alert from Dept 1 as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert in Dept 1 is now read
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin should be able to mark any alert as read regardless of department."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert in Dept 2 is now read
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
