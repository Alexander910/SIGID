from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Users
        self.user1 = User.objects.create_user(
            username='user1', password='password', department=self.dept1, role='encargado'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password', department=self.dept2, role='encargado'
        )

        # Category
        self.cat = Category.objects.create(name='Cat')

        # Product in Dept 2
        self.prod2 = Product.objects.create(
            name='Prod 2', code='P2', category=self.cat, department=self.dept2, quantity=10
        )

        # Alert in Dept 2
        self.alert2 = Alert.objects.create(
            product=self.prod2, alert_type='stock_bajo', message='Low stock', is_read=False
        )

    def test_user1_cannot_mark_user2_alert_as_read(self):
        """Test that user1 cannot mark an alert from dept2 as read."""
        self.client.login(username='user1', password='password')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        # Should return 404 because it shouldn't find the alert in user1's department if filtered,
        # or we could implement a 403. Currently get_object_or_404 is used without filtering.
        # If the vulnerability exists, it will return 302 (redirect) and the alert will be read.

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User1 was able to mark User2's alert as read (IDOR!)")
        self.assertEqual(response.status_code, 404)
