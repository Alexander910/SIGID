from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.category = Category.objects.create(name="General")

        self.user1 = User.objects.create_user(
            username="user1",
            password="password123",
            role="encargado",
            department=self.dept1,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="password123",
            role="admin",
        )

        self.product1 = Product.objects.create(
            code="P1",
            name="Product 1",
            category=self.category,
            department=self.dept1,
            quantity=10,
            min_stock=5,
        )
        self.product2 = Product.objects.create(
            code="P2",
            name="Product 2",
            category=self.category,
            department=self.dept2,
            quantity=10,
            min_stock=5,
        )

        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type="stock_bajo",
            message="Stock bajo para P1",
            is_read=False,
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type="stock_bajo",
            message="Stock bajo para P2",
            is_read=False,
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """A non-admin user should receive 404 when marking an alert from another department."""
        self.client.login(username="user1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """A non-admin user should successfully mark an alert from their department as read."""
        self.client.login(username="user1", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """An admin user should be able to mark alerts from any department as read."""
        self.client.login(username="admin", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
