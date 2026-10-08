from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPTA')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPTB')

        # Create category
        self.category = Category.objects.create(name='General', description='General category')

        # Create products in different departments
        self.prod_a = Product.objects.create(
            name='Product A',
            code='PRODA',
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.prod_b = Product.objects.create(
            name='Product B',
            code='PRODB',
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Create users
        self.user_dept_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )
        self.user_admin = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type='stock_bajo',
            message='Alert product A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='stock_bajo',
            message='Alert product B',
            is_read=False
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Encargado of Dept A should NOT be able to mark Dept B's alert as read (IDOR protection)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404)

        # Verify alert_b remains unread
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Encargado of Dept A should be able to mark Dept A's alert as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        # Should redirect to alert list
        self.assertEqual(response.status_code, 302)

        # Verify alert_a is now read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin user should be able to mark any alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
