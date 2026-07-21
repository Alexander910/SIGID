from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Product, Category
from alertas.models import Alert

User = get_user_model()


class AlertSecurityTests(TestCase):
    """Pruebas de seguridad para evitar IDOR en alertas."""

    def setUp(self):
        # Crear departamentos
        self.dept_it = Department.objects.create(name="IT", code="IT")
        self.dept_hr = Department.objects.create(name="HR", code="HR")

        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username="admin",
            password="password123",
            role="admin",
            is_staff=True,
            is_superuser=True
        )
        self.it_user = User.objects.create_user(
            username="it_user",
            password="password123",
            role="encargado",
            department=self.dept_it
        )
        self.hr_user = User.objects.create_user(
            username="hr_user",
            password="password123",
            role="encargado",
            department=self.dept_hr
        )

        # Categoría
        self.category = Category.objects.create(name="Equipos")

        # Productos
        self.product_it = Product.objects.create(
            name="Laptop IT",
            code="LAP-IT",
            category=self.category,
            department=self.dept_it,
            quantity=10,
            min_stock=5
        )
        self.product_hr = Product.objects.create(
            name="Laptop HR",
            code="LAP-HR",
            category=self.category,
            department=self.dept_hr,
            quantity=10,
            min_stock=5
        )

        # Alertas
        self.alert_it = Alert.objects.create(
            product=self.product_it,
            alert_type="stock_bajo",
            message="Stock de Laptop IT bajo",
            is_read=False
        )
        self.alert_hr = Alert.objects.create(
            product=self.product_hr,
            alert_type="stock_bajo",
            message="Stock de Laptop HR bajo",
            is_read=False
        )

        self.client = Client()

    def test_admin_can_mark_any_alert_read(self):
        """Un administrador puede marcar cualquier alerta de cualquier departamento como leída."""
        self.client.login(username="admin", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_hr.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_hr.refresh_from_db()
        self.assertTrue(self.alert_hr.is_read)

    def test_user_can_mark_own_department_alert_read(self):
        """Un encargado puede marcar una alerta de su propio departamento como leída."""
        self.client.login(username="it_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_it.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_user_cannot_mark_other_department_alert_read(self):
        """Un encargado NO puede marcar una alerta de otro departamento como leída (recibe un 404)."""
        self.client.login(username="it_user", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_hr.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_hr.refresh_from_db()
        self.assertFalse(self.alert_hr.is_read)
