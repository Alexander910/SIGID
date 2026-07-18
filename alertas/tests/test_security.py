from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    """Pruebas de seguridad e IDOR para alertas."""

    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Crear usuarios
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
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Crear categorías y productos
        self.category = Category.objects.create(name='Categoría General')
        self.product_a = Product.objects.create(
            name='Prod A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=15
        )
        self.product_b = Product.objects.create(
            name='Prod B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=5,
            min_stock=10
        )

        # Crear alertas
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='stock_bajo',
            message='Alerta de stock bajo para Prod A'
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Alerta de stock bajo para Prod B'
        )

        self.client = Client()

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Un encargado puede marcar como leída una alerta de su propio departamento."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirección

        # Verificar estado en la BD
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        """Un encargado NO puede marcar como leída una alerta de otro departamento (retorna 404)."""
        self.client.login(username='user_a', password='password123')
        # user_a (Dept A) intenta acceder a alert_b (Dept B)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  # No encontrado (IDOR prevenido)

        # Verificar que NO se modificó en la BD
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        """Un administrador puede marcar como leída cualquier alerta."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
