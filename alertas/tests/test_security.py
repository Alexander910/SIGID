from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(username='user1', password='password', department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username='user2', password='password', department=self.dept2, role='encargado')

        self.product1 = Product.objects.create(name='Product 1', code='P1', department=self.dept1, quantity=10)
        self.product2 = Product.objects.create(name='Product 2', code='P2', department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.product1, alert_type='stock_bajo', message='Low stock')
        self.alert2 = Alert.objects.create(product=self.product2, alert_type='stock_bajo', message='Low stock')

        self.client = Client()

    def test_mark_read_idor_prevention(self):
        """Test that user1 cannot mark alert2 (from dept2) as read."""
        self.client.login(username='user1', password='password')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # This SHOULD fail with 404
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "Alert should remain unread after unauthorized attempt")

    def test_mark_read_authorized(self):
        """Test that user1 can mark their own alert as read."""
        self.client.login(username='user1', password='password')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302) # Redirects to alert list
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
