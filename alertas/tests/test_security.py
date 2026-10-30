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
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123',
            role='encargado',
            department=self.dept2
        )

        self.category = Category.objects.create(name='General')

        self.product1 = Product.objects.create(
            name='Product 1',
            code='P1',
            category=self.category,
            department=self.dept1,
            quantity=0
        )
        self.product2 = Product.objects.create(
            name='Product 2',
            code='P2',
            category=self.category,
            department=self.dept2,
            quantity=0
        )

        self.alert1 = Alert.objects.create(
            product=self.product1,
            alert_type='sin_stock',
            message='Product 1 out of stock',
            is_read=False
        )
        self.alert2 = Alert.objects.create(
            product=self.product2,
            alert_type='sin_stock',
            message='Product 2 out of stock',
            is_read=False
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """User from dept1 should get 404 when trying to mark dept2 alert as read."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User from dept1 can mark dept1 alert as read."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
