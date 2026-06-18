from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Crear usuarios
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123',
            department=self.dept1,
            role='encargado'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123',
            department=self.dept2,
            role='encargado'
        )

        # Crear productos
        self.product1 = Product.objects.create(
            name='Product 1',
            code='P1',
            department=self.dept1,
            quantity=10
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            code='P2',
            department=self.dept2,
            quantity=10
        )

        # Crear alertas
        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type='stock_bajo',
            message='Stock bajo para P1'
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message='Stock bajo para P2'
        )

        self.client = Client()

    def test_encargado_cannot_mark_alert_from_other_dept_as_read(self):
        """
        Verifica que un encargado no pueda marcar como leída una alerta
        que pertenece a otro departamento (IDOR).
        """
        self.client.login(username='user1', password='password123')

        # URL para marcar la alerta 2 (del Dept 2) como leída
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # Intentar marcar como leída mediante POST
        response = self.client.post(url)

        # Debería devolver 404 porque el objeto no debería encontrarse bajo el filtro de departamento
        self.assertEqual(response.status_code, 404)

        # La alerta 2 NO debería haberse marcado como leída
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "Un usuario pudo marcar como leída una alerta de otro departamento")
