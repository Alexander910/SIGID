from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
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

        # Create products and alerts
        self.category = Category.objects.create(name="General")
        self.product_dept1 = Product.objects.create(
            code="P1",
            name="Prod Dept 1",
            category=self.category,
            department=self.dept1,
            quantity=0,
            min_stock=5
        )
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1,
            alert_type="sin_stock",
            message="No stock"
        )

    def test_idor_prevented_for_other_department_alert(self):
        """User from dept 2 should receive 404 when marking dept 1 alert as read."""
        self.client.login(username="user_dept2", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_dept1.refresh_from_db()
        self.assertFalse(self.alert_dept1.is_read)

    def test_mark_read_allowed_for_own_department(self):
        """User from dept 1 should successfully mark dept 1 alert as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_mark_read_allowed_for_admin(self):
        """Admin user should successfully mark any alert as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)
