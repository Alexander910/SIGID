from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    """Pruebas de seguridad para evitar IDOR en Alertas."""

    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        # Crear usuarios
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            email='user_a@test.com',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            email='user_b@test.com',
            role='encargado',
            department=self.dept_b
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            email='admin@test.com',
            role='admin'
        )

        # Crear productos
        self.product_a = Product.objects.create(
            name='Product A',
            code='P01',
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name='Product B',
            code='P02',
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Crear alertas
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='stock_bajo',
            message='Alerta Producto A'
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Alerta Producto B'
        )

    def test_encargado_can_mark_own_alert_as_read(self):
        """Un encargado puede marcar como leída una alerta de su propio departamento."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        # Debe redirigir a la lista de alertas
        self.assertEqual(response.status_code, 302)

        # Comprobar que la alerta se marcó como leída
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_encargado_cannot_mark_other_alert_as_read(self):
        """Un encargado no puede marcar como leída una alerta de otro departamento (IDOR)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Debe retornar 404 No Encontrado
        self.assertEqual(response.status_code, 404)

        # Comprobar que la alerta de otro departamento sigue sin leerse
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Un administrador puede marcar como leída cualquier alerta."""
        self.client.login(username='admin_user', password='password123')

        # Marcar alerta A (de Dept A)
        url_a = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response_a = self.client.post(url_a)
        self.assertEqual(response_a.status_code, 302)

        # Marcar alerta B (de Dept B)
        url_b = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response_b = self.client.post(url_b)
        self.assertEqual(response_b.status_code, 302)

        # Ambas alertas deben estar leídas
        self.alert_a.refresh_from_db()
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)
        self.assertTrue(self.alert_b.is_read)
