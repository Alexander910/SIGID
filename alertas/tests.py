from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from .models import Alert

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a', password='password123',
            department=self.dept_a, role='encargado'
        )
        self.user_b = User.objects.create_user(
            username='user_b', password='password123',
            department=self.dept_b, role='encargado'
        )

        # Create products
        self.prod_a = Product.objects.create(
            name='Prod A', code='PA', department=self.dept_a, quantity=10
        )
        self.prod_b = Product.objects.create(
            name='Prod B', code='PB', department=self.dept_b, quantity=10
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a, alert_type='stock_bajo', message='Low stock A'
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b, alert_type='stock_bajo', message='Low stock B'
        )

    def test_unauthorized_mark_read_idor(self):
        """
        Test that a user from Dept A cannot mark an alert from Dept B as read.
        """
        self.client.login(username='user_a', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        # This SHOULD return 404 if fixed, but currently likely returns 302 (redirect)
        # because it doesn't check department.
        response = self.client.post(url)

        self.alert_b.refresh_from_db()

        # Current state: it will be True and response 302.
        # Desired state: it should be False and response 404.
        if response.status_code == 302 and self.alert_b.is_read:
            print("\nVULNERABILITY CONFIRMED: User A marked Alert B as read!")

        self.assertEqual(response.status_code, 404, "IDOR Vulnerability: User marked an alert from another department as read.")
        self.assertFalse(self.alert_b.is_read)

    def test_authorized_mark_read(self):
        """
        Test that a user can mark an alert from their own department as read.
        """
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_mark_read_any_department(self):
        """
        Test that an admin can mark any alert as read.
        """
        admin = User.objects.create_superuser(
            username='admin', password='password123', email='admin@test.com'
        )
        self.client.login(username='admin', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
