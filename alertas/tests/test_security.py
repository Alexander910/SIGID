from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a', password='password',
            department=self.dept_a, role='encargado'
        )
        self.user_b = User.objects.create_user(
            username='user_b', password='password',
            department=self.dept_b, role='encargado'
        )

        # Create category
        self.cat = Category.objects.create(name='Cat')

        # Create products
        self.prod_a = Product.objects.create(
            name='Prod A', code='PA', category=self.cat,
            department=self.dept_a, quantity=10
        )
        self.prod_b = Product.objects.create(
            name='Prod B', code='PB', category=self.cat,
            department=self.dept_b, quantity=10
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a, alert_type='stock_bajo', message='Low stock A'
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b, alert_type='stock_bajo', message='Low stock B'
        )

    def test_idor_alert_mark_read(self):
        """Test that user_a cannot mark alert_b as read."""
        self.client.login(username='user_a', password='password')

        # User A tries to mark Alert B (from Dept B) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # In a secure system, this should probably return 404 or 403
        # Currently it probably returns 302 (redirect) and marks it as read

        self.alert_b.refresh_from_db()
        if self.alert_b.is_read:
            self.fail("IDOR VULNERABILITY: User A marked alert of Dept B as read!")

        self.assertEqual(response.status_code, 404)
