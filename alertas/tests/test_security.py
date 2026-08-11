from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password123',
            role='admin'
        )
        self.user_a = User.objects.create_user(
            username='user_a',
            email='usera@test.com',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            email='userb@test.com',
            password='password123',
            role='encargado',
            department=self.dept_b
        )

        # Create products
        self.prod_a = Product.objects.create(
            name='Product A',
            code='P-A',
            department=self.dept_a
        )
        self.prod_b = Product.objects.create(
            name='Product B',
            code='P-B',
            department=self.dept_b
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='sin_stock',
            message='Stock has run out for P-A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='sin_stock',
            message='Stock has run out for P-B',
            is_read=False
        )

    def test_admin_can_mark_any_alert_read(self):
        client = Client()
        client.login(username='admin', password='password123')

        # Admin marks alert_a as read
        response = client.post(reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk}))
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_user_can_mark_own_department_alert_read(self):
        client = Client()
        client.login(username='user_a', password='password123')

        # User A marks alert_a as read (same department)
        response = client.post(reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk}))
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_user_cannot_mark_other_department_alert_read(self):
        client = Client()
        client.login(username='user_a', password='password123')

        # User A tries to mark alert_b as read (different department)
        response = client.post(reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk}))
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)
