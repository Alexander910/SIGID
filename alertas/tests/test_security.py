from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
        self.encargado1 = User.objects.create_user(
            username="encargado1",
            password="password123",
            role="encargado",
            department=self.dept1,
        )
        self.encargado2 = User.objects.create_user(
            username="encargado2",
            password="password123",
            role="encargado",
            department=self.dept2,
        )
        self.admin = User.objects.create_user(
            username="adminuser",
            password="password123",
            role="admin",
        )

        # Create category and products
        self.category = Category.objects.create(name="Cat 1", description="Cat Desc")
        self.prod1 = Product.objects.create(
            name="Prod 1",
            code="P1",
            category=self.category,
            department=self.dept1,
            quantity=5,
            min_stock=10,
        )
        self.prod2 = Product.objects.create(
            name="Prod 2",
            code="P2",
            category=self.category,
            department=self.dept2,
            quantity=5,
            min_stock=10,
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.prod1,
            alert_type="stock_bajo",
            message="Low stock on Prod 1",
            is_read=False,
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.prod2,
            alert_type="stock_bajo",
            message="Low stock on Prod 2",
            is_read=False,
        )

    def test_idor_prevented_when_marking_alert_from_other_department(self):
        """User from dept1 cannot mark alert from dept2 as read (should return 404)."""
        self.client.login(username="encargado1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verify alert remained unread
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User from dept1 can mark alert from dept1 as read."""
        self.client.login(username="encargado1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin can mark alerts from any department as read."""
        self.client.login(username="adminuser", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_dept2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
