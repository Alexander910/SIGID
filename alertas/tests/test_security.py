from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(username='user1', password='pass', role='encargado', department=self.dept1)
        self.user2 = User.objects.create_user(username='user2', password='pass', role='encargado', department=self.dept2)

        self.prod1 = Product.objects.create(name='Prod 1', code='P1', department=self.dept1, quantity=10)
        self.prod2 = Product.objects.create(name='Prod 2', code='P2', department=self.dept2, quantity=10)

        self.alert1 = Alert.objects.create(product=self.prod1, message='Alert 1')
        self.alert2 = Alert.objects.create(product=self.prod2, message='Alert 2')

    def test_idor_mark_read_different_department(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username='user1', password='pass')

        # User 1 tries to mark Alert 2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # This should now return 404
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        # It should remain unread
        self.assertFalse(self.alert2.is_read, "User should not be able to mark an alert from another department as read.")

    def test_admin_can_mark_any_alert_as_read(self):
        """Test that an admin can mark any alert as read, regardless of department."""
        admin = User.objects.create_superuser(username='admin', password='pass', role='admin')
        self.client.login(username='admin', password='pass')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
