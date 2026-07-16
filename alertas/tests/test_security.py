from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Crear usuarios
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            department=self.dept_a,
            role='encargado'
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            department=self.dept_b,
            role='encargado'
        )

        # Crear categoría
        self.cat = Category.objects.create(name='General')

        # Crear producto en Dept B
        self.product_b = Product.objects.create(
            name='Product B',
            code='PB',
            category=self.cat,
            department=self.dept_b,
            quantity=10
        )

        # Crear alerta para Product B
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Stock bajo en Product B',
            is_read=False
        )

        self.client = Client()

    def test_idor_mark_alert_read(self):
        """
        Verifica que un usuario no pueda marcar como leída una alerta
        de un producto que no pertenece a su departamento.
        """
        self.client.login(username='user_a', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        # Intentar marcar como leída la alerta del Dept B siendo del Dept A
        response = self.client.post(url)

        # Refrescar alerta desde DB
        self.alert_b.refresh_from_db()

        # Si hay IDOR, la alerta se marcará como leída y probablemente redirigirá (302)
        # El comportamiento esperado tras el fix debería ser 404
        self.assertEqual(response.status_code, 404, "Debe retornar 404 al intentar acceder a una alerta de otro departamento")
        self.assertFalse(self.alert_b.is_read, "La alerta no debe marcarse como leída")
