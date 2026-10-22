from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Dept B', code='DEPT_B')

        # Create user for Dept A
        self.user_a = User.objects.create_user(
            username='user_a',
            password='Password123!',
            role='encargado',
            department=self.dept_a
        )

        # Create category & products
        self.category = Category.objects.create(name='General', description='General category')
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
            message='Alert A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type='sin_stock',
            message='Alert B',
            is_read=False
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify that a user cannot mark an alert from another department as read (IDOR prevention)."""
        self.client.login(username='user_a', password='Password123!')

        # Attempt to mark Dept B's alert as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Should return 404 Not Found
        self.assertEqual(response.status_code, 404)

        # Verify alert_b remains unread
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Verify that a user can mark an alert from their own department as read."""
        self.client.login(username='user_a', password='Password123!')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        # Should redirect to alert list
        self.assertEqual(response.status_code, 302)

        # Verify alert_a is marked as read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)
