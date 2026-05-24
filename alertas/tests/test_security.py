from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            department=self.dept_a,
            role='encargado'
        )

        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            department=self.dept_b,
            role='encargado'
        )

        self.category = Category.objects.create(name='Cat')

        self.product_b = Product.objects.create(
            name='Product B',
            code='PB',
            category=self.category,
            department=self.dept_b,
            quantity=10
        )

        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='stock_bajo',
            message='Low stock on product B'
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Test that a user from Dept A cannot mark an alert from Dept B as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Test that a user can mark an alert from their own department as read."""
        self.client.login(username='user_b', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
