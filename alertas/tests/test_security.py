from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass', role='encargado', department=self.dept1)
        self.user2 = User.objects.create_user(username='user2', password='pass', role='encargado', department=self.dept2)

        # Create products
        self.prod1 = Product.objects.create(name='Prod 1', code='S1', department=self.dept1, quantity=10)
        self.prod2 = Product.objects.create(name='Prod 2', code='S2', department=self.dept2, quantity=10)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, alert_type='stock_bajo', message='Low stock on P1')
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type='stock_bajo', message='Low stock on P2')

    def test_idor_mark_read_different_department(self):
        """Test that a user cannot mark an alert from another department as read."""
        self.client.login(username='user1', password='pass')

        # User 1 tries to mark Alert 2 (from Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Check database state
        self.alert2.refresh_from_db()

        if response.status_code == 302 and self.alert2.is_read:
            print("\nVULNERABILITY CONFIRMED: User 1 was able to mark Alert 2 as read!")

        # Verification
        self.assertEqual(response.status_code, 404, "Should return 404 for alert in different department")
        self.assertFalse(self.alert2.is_read, "Alert should not be marked as read")
