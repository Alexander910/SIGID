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
            email="u1@test.com",
            password="password123",
            role="encargado",
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username="user_dept2",
            email="u2@test.com",
            password="password123",
            role="encargado",
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@test.com",
            password="password123",
            role="admin"
        )

        # Create Category
        self.category = Category.objects.create(name="General")

        # Create Products
        self.product1 = Product.objects.create(
            code="P1",
            name="Prod 1",
            category=self.category,
            department=self.dept1,
            quantity=1,
            min_stock=5
        )
        self.product2 = Product.objects.create(
            code="P2",
            name="Prod 2",
            category=self.category,
            department=self.dept2,
            quantity=1,
            min_stock=5
        )

        # Create Alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product1,
            alert_type="stock_bajo",
            message="Low stock on P1",
            is_read=False
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product2,
            alert_type="stock_bajo",
            message="Low stock on P2",
            is_read=False
        )

    def test_idor_prevented_for_other_department_alert(self):
        """Non-admin user should receive 404 when marking an alert from another department as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verify alert remains unread in database
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_read(self):
        """Non-admin user can successfully mark an alert from their own department as read."""
        self.client.login(username="user_dept1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify alert is now read
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_department_alert_read(self):
        """Admin user can mark alerts from any department as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify alert is now read
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
