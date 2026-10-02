from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create Users
        self.user_dept1 = User.objects.create_user(
            username="user_dept1",
            password="password123",
            role="encargado",
            department=self.dept1,
        )
        self.user_dept2 = User.objects.create_user(
            username="user_dept2",
            password="password123",
            role="encargado",
            department=self.dept2,
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin",
            department=self.dept1,
        )

        # Create Products
        self.product_dept1 = Product.objects.create(
            name="Prod 1", code="P1", department=self.dept1, quantity=0, min_stock=5
        )
        self.product_dept2 = Product.objects.create(
            name="Prod 2", code="P2", department=self.dept2, quantity=0, min_stock=5
        )

        # Create Alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product_dept1, alert_type="sin_stock", message="No stock"
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product_dept2, alert_type="sin_stock", message="No stock"
        )

    def test_idor_prevented_for_other_department_alert(self):
        """Ensure user from Dept 1 cannot mark Dept 2 alert as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Ensure user from Dept 1 can mark Dept 1 alert as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Ensure admin can mark alerts from any department as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
