from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name="Dept A", code="DA")
        self.dept_b = Department.objects.create(name="Dept B", code="DB")

        # Crear usuarios
        self.user_a = User.objects.create_user(
            username="user_a",
            password="password123",
            role="encargado",
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            password="password123",
            role="encargado",
            department=self.dept_b
        )
        self.admin = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin"
        )

        # Crear categorías y productos
        self.category = Category.objects.create(name="General")
        self.product_a = Product.objects.create(
            code="P001",
            name="Product A",
            category=self.category,
            department=self.dept_a,
            quantity=1,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            code="P002",
            name="Product B",
            category=self.category,
            department=self.dept_b,
            quantity=1,
            min_stock=5
        )

        # Crear alertas
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Stock bajo A"
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Stock bajo B"
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Un usuario de Dept A no debe poder marcar como leída una alerta de Dept B (IDOR)."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Un usuario de Dept A puede marcar como leída una alerta de su departamento."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Un admin puede marcar cualquier alerta como leída."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
