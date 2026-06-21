from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(username='user1', password='password', department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username='user2', password='password', department=self.dept2, role='encargado')

        self.prod1 = Product.objects.create(name='Prod 1', department=self.dept1, code='S1')
        self.prod2 = Product.objects.create(name='Prod 2', department=self.dept2, code='S2')

        self.alert1 = Alert.objects.create(product=self.prod1, message='Alert 1')
        self.alert2 = Alert.objects.create(product=self.prod2, message='Alert 2')

    def test_idor_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username='user1', password='password')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # This should ideally fail or not find the object
        response = self.client.post(url)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 marked User 2's alert as read!")
        self.assertEqual(response.status_code, 404)
