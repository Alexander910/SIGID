from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Department A', code='DEPT_A')
        self.dept_b = Department.objects.create(name='Department B', code='DEPT_B')

        # Create category
        self.category = Category.objects.create(name='General', description='General category')

        # Create products in different departments
        self.product_a = Product.objects.create(
            code='PROD_A',
            name='Product A',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            code='PROD_B',
            name='Product B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Alert A',
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Alert B',
            is_read=False
        )

        # Create user in Dept A
        self.user_a = User.objects.create_user(
            username='user_a',
            password='password123',
            role='encargado',
            department=self.dept_a
        )

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Test non-admin user cannot mark an alert from another department as read (IDOR check)."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Expect 404 Not Found due to get_object_or_404 on department-filtered queryset
        self.assertEqual(response.status_code, 404)

        # Ensure alert_b is still unread
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """Test user can mark an alert from their own department as read."""
        self.client.login(username='user_a', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Test admin can mark any alert as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
