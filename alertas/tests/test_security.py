from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Department A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Department B", code="DEPTB")

        # Create users
        self.admin_user = User.objects.create_user(
            username="admin",
            password="password",
            role="admin",
            is_superuser=True
        )
        self.user_a = User.objects.create_user(
            username="usera",
            password="password",
            role="encargado",
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="userb",
            password="password",
            role="encargado",
            department=self.dept_b
        )

        # Create products
        self.product_a = Product.objects.create(
            name="Product A",
            code="PRODA",
            department=self.dept_a,
            quantity=10
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PRODB",
            department=self.dept_b,
            quantity=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Stock bajo para Product A"
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="sin_stock",
            message="Sin stock para Product B"
        )

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username="admin", password="password")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        self.client.login(username="usera", password="password")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_user_cannot_mark_other_department_alert_as_read_idor(self):
        self.client.login(username="usera", password="password")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)
        # Should fail with 404
        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        # Ensure it remains unread
        self.assertFalse(self.alert_b.is_read)
