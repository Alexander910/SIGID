from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='password123',
            role='encargado',
            department=self.dept_b,
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin',
        )

        self.category = Category.objects.create(name='Cat 1')
        self.product_b = Product.objects.create(
            code='PRODB',
            name='Product B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Sin stock en Dept B',
            is_read=False,
        )

    def test_idor_alert_mark_read_unauthorized(self):
        """User A from Dept A should NOT be able to mark Dept B's alert as read (404)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_idor_alert_mark_read_authorized(self):
        """User B from Dept B should be able to mark Dept B's alert as read."""
        self.client.login(username='user_b', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_idor_alert_mark_read_admin(self):
        """Admin user should be able to mark any alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
