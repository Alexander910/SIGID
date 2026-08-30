from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

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
        self.admin = User.objects.create_user(
            username='adminuser',
            password='password123',
            role='admin'
        )

        self.category = Category.objects.create(name='General')
        self.prod1 = Product.objects.create(
            name='Prod 1',
            code='P1',
            quantity=10,
            department=self.dept1,
            category=self.category
        )
        self.prod2 = Product.objects.create(
            name='Prod 2',
            code='P2',
            quantity=10,
            department=self.dept2,
            category=self.category
        )

        self.alert_dept1 = Alert.objects.create(
            product=self.prod1,
            alert_type='stock_bajo',
            message='Stock bajo prod 1',
            is_read=False
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.prod2,
            alert_type='stock_bajo',
            message='Stock bajo prod 2',
            is_read=False
        )

        self.client = Client()

    def test_non_admin_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_non_admin_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='adminuser', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
