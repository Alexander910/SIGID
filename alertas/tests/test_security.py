from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class SecurityIDORTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            role='encargado',
            department=self.dept_b
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create category and products
        self.category = Category.objects.create(name='General')
        self.prod_a = Product.objects.create(
            name='Product A',
            code='PROD_A',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        self.prod_b = Product.objects.create(
            name='Product B',
            code='PROD_B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='sin_stock',
            message='Stock depleted A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='sin_stock',
            message='Stock depleted B',
            is_read=False
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verify state is unchanged
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify state changed
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify state changed
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
