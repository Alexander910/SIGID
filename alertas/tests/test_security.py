from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    """Tests para verificar la seguridad e IDOR en las alertas."""

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

        # Crear productos y alertas
        self.category = Category.objects.create(name="Cat 1")
        self.product_a = Product.objects.create(
            name="Prod A",
            code="P-A",
            category=self.category,
            department=self.dept_a,
            quantity=0
        )
        self.product_b = Product.objects.create(
            name="Prod B",
            code="P-B",
            category=self.category,
            department=self.dept_b,
            quantity=0
        )

        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="sin_stock",
            message="Sin stock Prod A"
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="sin_stock",
            message="Sin stock Prod B"
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Un usuario de Dept A no debe poder marcar como leída una alerta de Dept B."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verificar en DB que la alerta sigue sin leer
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Un usuario de Dept A puede marcar como leída una alerta de su departamento."""
        self.client.login(username="user_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verificar en DB que la alerta fue marcada como leída
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """El administrador puede marcar como leída cualquier alerta."""
        self.client.login(username="admin_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verificar en DB que la alerta fue marcada como leída
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
