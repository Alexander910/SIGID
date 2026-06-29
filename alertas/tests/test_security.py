from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(
            username='user1', password='password', department=self.dept1, role='encargado'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password', department=self.dept2, role='encargado'
        )

        self.product1 = Product.objects.create(name='P1', code='C1', department=self.dept1, quantity=10)
        self.product2 = Product.objects.create(name='P2', code='C2', department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.product1, message='Alert 1')
        self.alert2 = Alert.objects.create(product=self.product2, message='Alert 2')

        self.client1 = Client()
        self.client1.login(username='user1', password='password')

    def test_idor_alert_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client1.post(url)

        # This should fail if the vulnerability exists
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)
