from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='IT', code='IT01')
        self.dept2 = Department.objects.create(name='HR', code='HR01')

        self.user1 = User.objects.create_user(
            username='user_it',
            password='password123',
            role='encargado',
            department=self.dept1,
        )
        self.user2 = User.objects.create_user(
            username='user_hr',
            password='password123',
            role='encargado',
            department=self.dept2,
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.prod1 = Product.objects.create(
            name='Laptop',
            code='P01',
            department=self.dept1,
            quantity=0,
            min_stock=5,
        )
        self.prod2 = Product.objects.create(
            name='Printer Paper',
            code='P02',
            department=self.dept2,
            quantity=0,
            min_stock=5,
        )

        self.alert_dept2 = Alert.objects.create(
            product=self.prod2,
            alert_type='sin_stock',
            message='Stock en 0',
            is_read=False,
        )

    def test_user_cannot_mark_alert_read_from_another_department(self):
        # Security test: User in dept1 attempts IDOR to mark dept2 alert as read
        self.client.login(username='user_it', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user_hr', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
