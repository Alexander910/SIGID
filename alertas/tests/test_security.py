from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        # Crear usuarios (encargados)
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            role='encargado',
            department=self.dept_b
        )

        # Crear producto en Dept B
        self.product_b = Product.objects.create(
            name='Product B',
            code='PB',
            department=self.dept_b,
            quantity=10
        )

        # Crear alerta para el producto en Dept B
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Stock bajo en B'
        )

        self.client_a = Client()
        self.client_a.login(username='user_a', password='password123')

    def test_idor_mark_alert_read_other_department(self):
        """
        Verifica que un usuario no pueda marcar como leída una alerta
        de otro departamento.
        """
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        # Intentar marcar como leída
        response = self.client_a.post(url)

        # Actualmente es vulnerable, así que esto fallará (devolverá 302 en lugar de 404)
        self.assertEqual(response.status_code, 404)

        # Verificar que la alerta SIGUE sin estar leída
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)
