from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(
            username='user1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )

        self.product1 = Product.objects.create(
            name='Product 1',
            code='P1',
            department=self.dept1,
            quantity=5
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            code='P2',
            department=self.dept2,
            quantity=5
        )

        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type='stock_bajo',
            message='Stock bajo en Product 1'
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message='Stock bajo en Product 2'
        )

    def test_user_cannot_mark_other_dept_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_dept_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
