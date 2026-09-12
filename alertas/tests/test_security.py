from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(
            username='user1',
            password='password123',
            role='encargado',
            department=self.dept1,
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123',
            role='encargado',
            department=self.dept2,
        )
        self.admin = User.objects.create_user(
            username='adminuser',
            password='password123',
            role='admin',
            is_superuser=True,
        )

        self.category = Category.objects.create(name='General')

        self.prod1 = Product.objects.create(
            name='Product 1',
            code='P1',
            department=self.dept1,
            category=self.category,
            quantity=0,
            min_stock=5,
        )
        self.prod2 = Product.objects.create(
            name='Product 2',
            code='P2',
            department=self.dept2,
            category=self.category,
            quantity=0,
            min_stock=5,
        )

        self.alert1 = Alert.objects.create(
            product=self.prod1,
            alert_type='sin_stock',
            message='Product 1 is out of stock',
            is_read=False,
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type='sin_stock',
            message='Product 2 is out of stock',
            is_read=False,
        )

    def test_user_cannot_mark_other_department_alert_read(self):
        """User from dept 1 cannot mark alert from dept 2 as read (IDOR prevention)."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_department_alert_read(self):
        """User from dept 1 can mark alert from dept 1 as read."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Admin user can mark alerts from any department as read."""
        self.client.login(username='adminuser', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
