from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Crear departamentos
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Crear usuarios (encargados)
        self.user1 = User.objects.create_user(
            username='user1', password='password123',
            role='encargado', department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password123',
            role='encargado', department=self.dept2
        )

        # Crear categoría
        self.cat = Category.objects.create(name='Cat 1')

        # Crear productos
        self.prod1 = Product.objects.create(
            name='Prod 1', code='P1', category=self.cat,
            department=self.dept1, quantity=10, min_stock=5
        )
        self.prod2 = Product.objects.create(
            name='Prod 2', code='P2', category=self.cat,
            department=self.dept2, quantity=10, min_stock=5
        )

        # Crear alertas
        self.alert1 = Alert.objects.create(
            product=self.prod1, alert_type='stock_bajo', message='Bajo'
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2, alert_type='stock_bajo', message='Bajo'
        )

    def test_idor_mark_alert_read(self):
        """
        Un usuario no debería poder marcar como leída una alerta
        que pertenece a otro departamento.
        """
        self.client.login(username='user1', password='password123')

        # Intentar marcar alerta del Dept 2 como leída
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Debería devolver 404 (o 403, pero get_object_or_404 da 404)
        # Actualmente fallará porque devolverá 302 (redirect) y la alerta será marcada como leída.

        self.alert2.refresh_from_db()
        self.assertEqual(response.status_code, 404, "Debería devolver 404 para alertas de otro departamento")
        self.assertFalse(self.alert2.is_read, "La alerta no debería haber sido marcada como leída")
