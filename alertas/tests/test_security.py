from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass1', department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username='user2', password='pass2', department=self.dept2, role='encargado')

        # Create products
        self.prod1 = Product.objects.create(name='Prod 1', code='P1', department=self.dept1, quantity=0)
        self.prod2 = Product.objects.create(name='Prod 2', code='P2', department=self.dept2, quantity=0)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, alert_type='sin_stock', message='Out of stock')
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type='sin_stock', message='Out of stock')

    def test_idor_mark_read_single_alert(self):
        """Test that user1 cannot mark alert2 as read because it belongs to dept2."""
        self.client.login(username='user1', password='pass1')

        # Try to mark alert2 as read (should fail or at least not change it)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Current implementation probably returns 302 and marks it as read
        self.alert2.refresh_from_db()

        # For a proper test, we want it to NOT be read
        self.assertFalse(self.alert2.is_read, "IDOR Vulnerability: User marked an alert from another department as read")

    def test_mark_all_read_isolation(self):
        """Test that AlertMarkAllReadView only marks alerts for the user's department."""
        self.client.login(username='user1', password='pass1')

        url = reverse('alertas:alert_mark_all_read')
        self.client.post(url)

        self.alert1.refresh_from_db()
        self.alert2.refresh_from_db()

        self.assertTrue(self.alert1.is_read)
        self.assertFalse(self.alert2.is_read, "IDOR Vulnerability: AlertMarkAllRead marked alerts from another department")
