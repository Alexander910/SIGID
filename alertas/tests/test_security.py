from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    """Pruebas de seguridad para verificar mitigación de IDOR en alertas."""

    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name="Depto A", code="DEPT-A")
        self.dept_b = Department.objects.create(name="Depto B", code="DEPT-B")

        # Crear usuarios con rol encargado
        self.user_a = User.objects.create_user(
            username="encargado_a",
            password="password123",
            role="encargado",
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="encargado_b",
            password="password123",
            role="encargado",
            department=self.dept_b
        )

        # Crear administrador
        self.admin = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin"
        )

        # Crear categoría
        self.category = Category.objects.create(name="Categoría General")

        # Crear productos
        self.product_a = Product.objects.create(
            name="Producto A",
            code="PROD-A",
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name="Producto B",
            code="PROD-B",
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Crear alertas
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Alerta de stock bajo para Producto A"
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Alerta de stock bajo para Producto B"
        )

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Un encargado puede marcar como leída una alerta de su propio departamento."""
        self.client.login(username="encargado_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirección exitosa

        # Verificar que el estado de la alerta cambió
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_encargado_cannot_mark_other_department_alert_as_read_idor(self):
        """Un encargado no puede marcar como leída una alerta de otro departamento (IDOR)."""
        self.client.login(username="encargado_a", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  # Debe retornar un 404 No Encontrado

        # Verificar que la alerta NO fue marcada como leída
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        """Un administrador puede marcar como leída cualquier alerta de cualquier departamento."""
        self.client.login(username="admin_user", password="password123")

        # Marcar alerta del departamento B como leída siendo admin
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
