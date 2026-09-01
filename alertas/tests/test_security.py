from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name="Dept A", code="DA")
        self.dept_b = Department.objects.create(name="Dept B", code="DB")

        # Crear usuarios para cada departamento
        self.user_a = User.objects.create_user(
            username="user_a",
            password="password123",
            role="encargado",
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            password="password123",
            role="encargado",
            department=self.dept_b,
        )

        # Crear productos para cada departamento
        self.prod_a = Product.objects.create(
            name="Product A",
            code="PA",
            department=self.dept_a,
            quantity=0,
            min_stock=5,
        )
        self.prod_b = Product.objects.create(
            name="Product B",
            code="PB",
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )

        # Crear alerta en departamento B
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type="sin_stock",
            message="Sin stock en Producto B",
            is_read=False,
        )

        self.client_a = Client()
        self.client_a.login(username="user_a", password="password123")

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """User A from Dept A should not be able to mark Alert B (Dept B) as read (IDOR prevention)."""
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client_a.post(url)

        # Se espera un 404 Not Found debido al filtrado de departamento
        self.assertEqual(response.status_code, 404)

        # Verificar que la alerta no se marcó como leída en la BD
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)
