from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(username='user1', password='pass', department=self.dept1, role='encargado')
        self.user2 = User.objects.create_user(username='user2', password='pass', department=self.dept2, role='encargado')

        self.prod1 = Product.objects.create(name='Prod 1', code='P1', department=self.dept1, quantity=10, min_stock=5)
        self.prod2 = Product.objects.create(name='Prod 2', code='P2', department=self.dept2, quantity=10, min_stock=5)

        self.alert1 = Alert.objects.create(product=self.prod1, message='Low stock 1')
        self.alert2 = Alert.objects.create(product=self.prod2, message='Low stock 2')

        self.client1 = Client()
        self.client1.login(username='user1', password='pass')

    def test_idor_mark_read(self):
        """Test that user1 cannot mark alert2 as read."""
        response = self.client1.post(reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk}))
        # It should probably return 404 or 403, but currently it likely returns 302 and marks it read
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User 1 marked User 2's alert as read!")
