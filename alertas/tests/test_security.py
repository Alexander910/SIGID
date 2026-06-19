from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name="Dept A", code="A")
        self.dept_b = Department.objects.create(name="Dept B", code="B")

        # Crear usuarios encargados
        self.user_a = User.objects.create_user(
            username="user_a", password="password123",
            role="encargado", department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="user_b", password="password123",
            role="encargado", department=self.dept_b
        )

        # Crear categoría y producto para Dept A
        self.cat = Category.objects.create(name="Cat 1")
        self.prod_a = Product.objects.create(
            name="Prod A", code="PA", category=self.cat,
            department=self.dept_a, quantity=10
        )

        # Crear alerta para Dept A
        self.alert_a = Alert.objects.create(
            product=self.prod_a, alert_type="stock_bajo",
            message="Stock bajo para Prod A"
        )

        self.client_b = Client()
        self.client_b.login(username="user_b", password="password123")

    def test_idor_mark_alert_read(self):
        """
        Verificar que un usuario de Dept B NO puede marcar como leída
        una alerta de Dept A.
        """
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        # Intento de marcar como leída
        response = self.client_b.post(url)

        # Debe devolver 404 si el sistema es seguro
        self.assertEqual(response.status_code, 404)

        self.alert_a.refresh_from_db()
        self.assertFalse(self.alert_a.is_read, "SECURED: User B was NOT able to mark Alert A as read.")
