from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Product
from alertas.models import Alert

User = get_user_model()

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='Dept One', code='D1')
        self.dept2 = Department.objects.create(name='Dept Two', code='D2')

        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123',
            role='encargado',
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create products
        self.prod1 = Product.objects.create(
            name='Product One',
            code='P1',
            department=self.dept1,
            quantity=10,
            min_stock=5
        )
        self.prod2 = Product.objects.create(
            name='Product Two',
            code='P2',
            department=self.dept2,
            quantity=10,
            min_stock=5
        )

        # Create alerts
        self.alert1 = Alert.objects.create(
            product=self.prod1,
            alert_type='stock_bajo',
            message='Stock is low for product one',
            is_read=False
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type='stock_bajo',
            message='Stock is low for product two',
            is_read=False
        )

    def test_encargado_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)

        # Verify redirect
        self.assertEqual(response.status_code, 302)

        # Verify DB state updated
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_encargado_cannot_mark_other_department_alert_as_read_idor(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Verify 404 is returned to prevent IDOR
        self.assertEqual(response.status_code, 404)

        # Verify DB state remains unchanged
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin_user', password='password123')

        # Admin marks alert1 as read
        url1 = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response1 = self.client.post(url1)
        self.assertEqual(response1.status_code, 302)
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

        # Admin marks alert2 as read
        url2 = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response2 = self.client.post(url2)
        self.assertEqual(response2.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
