from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a', password='password', department=self.dept_a, role='encargado'
        )
        self.user_b = User.objects.create_user(
            username='user_b', password='password', department=self.dept_b, role='encargado'
        )

        # Create products
        self.prod_a = Product.objects.create(
            name='Prod A', code='PA', department=self.dept_a, quantity=10
        )
        self.prod_b = Product.objects.create(
            name='Prod B', code='PB', department=self.dept_b, quantity=10
        )

        # Create alert for Dept B
        self.alert_b = Alert.objects.create(
            product=self.prod_b, alert_type='stock_bajo', message='Bajo stock B'
        )

    def test_unauthorized_mark_read(self):
        """User A should NOT be able to mark Dept B's alert as read."""
        self.client.login(username='user_a', password='password')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        # Try to mark as read
        response = self.client.post(url)

        # It should return 404 because User A shouldn't see/access Dept B's alert
        # Current implementation will return 302 (redirect) because it's vulnerable

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read, "User A managed to mark Dept B's alert as read!")
        self.assertEqual(response.status_code, 404)
