from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

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

        self.cat = Category.objects.create(name='Cat 1')

        self.prod_a = Product.objects.create(
            name='Prod A', code='P001', category=self.cat, department=self.dept_a, quantity=0, min_stock=10
        )
        self.prod_b = Product.objects.create(
            name='Prod B', code='P002', category=self.cat, department=self.dept_b, quantity=0, min_stock=10
        )

        self.alert_a = Alert.objects.create(
            product=self.prod_a, alert_type='sin_stock', message='Out of stock A', is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b, alert_type='sin_stock', message='Out of stock B', is_read=False
        )

    def test_idor_mark_alert_read_cross_department(self):
        """Verify user A cannot mark alert B (other department) as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Non-admin user accessing alert of another department should get 404
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_own_department_mark_alert_read(self):
        """Verify user A can mark alert A (own department) as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)
