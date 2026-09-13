from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123',
            role='encargado',
            department=self.dept2
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='password123',
            role='admin'
        )

        self.cat = Category.objects.create(name='Cat 1')
        self.product1 = Product.objects.create(
            name='Prod 1',
            code='P1',
            category=self.cat,
            department=self.dept1,
            quantity=5,
            min_stock=10
        )
        self.product2 = Product.objects.create(
            name='Prod 2',
            code='P2',
            category=self.cat,
            department=self.dept2,
            quantity=5,
            min_stock=10
        )

        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type='stock_bajo',
            message='Stock bajo P1',
            is_read=False
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='stock_bajo',
            message='Stock bajo P2',
            is_read=False
        )

        self.client1 = Client()
        self.client1.login(username='user1', password='password123')

        self.admin_client = Client()
        self.admin_client.login(username='admin', password='password123')

    def test_user_cannot_mark_other_dept_alert_as_read(self):
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client1.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_dept_alert_as_read(self):
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client1.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.admin_client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
