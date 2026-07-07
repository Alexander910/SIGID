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
        self.user1 = User.objects.create_user(username='user1', password='pass', role='encargado', department=self.dept1)
        self.user2 = User.objects.create_user(username='user2', password='pass', role='encargado', department=self.dept2)

        # Create category
        self.cat = Category.objects.create(name='Cat')

        # Create products
        self.prod1 = Product.objects.create(name='Prod 1', code='P1', department=self.dept1, category=self.cat)
        self.prod2 = Product.objects.create(name='Prod 2', code='P2', department=self.dept2, category=self.cat)

        # Create alerts
        self.alert1 = Alert.objects.create(product=self.prod1, message='Alert 1')
        self.alert2 = Alert.objects.create(product=self.prod2, message='Alert 2')

        self.client = Client()

    def test_idor_alert_mark_read(self):
        """Test that a user cannot mark as read an alert from another department."""
        self.client.login(username='user1', password='pass')

        # Try to mark alert2 (Dept 2) as read using user1 (Dept 1)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # If it's vulnerable, it will redirect (302) and mark it as read.
        # If it's secure, it should probably return 404.

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User1 should NOT be able to mark alert2 as read.")
        self.assertEqual(response.status_code, 404, "Should return 404 for unauthorized alert access.")
