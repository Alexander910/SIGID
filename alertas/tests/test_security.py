"""
Tests for security and data isolation in the alertas app.
"""
from django.test import TestCase
from django.urls import reverse

from alertas.models import Alert
from inventario.models import Product, Category
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    """Test suite verifying IDOR protection on alert endpoints."""

    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(
            name='Dept A',
            code='DEPT-A',
        )
        self.dept_b = Department.objects.create(
            name='Dept B',
            code='DEPT-B',
        )

        # Create category
        self.category = Category.objects.create(
            name='General',
            description='General category',
        )

        # Create products in different departments
        self.product_a = Product.objects.create(
            name='Product A',
            code='PROD-A',
            category=self.category,
            department=self.dept_a,
            quantity=0,
            min_stock=5,
        )
        self.product_b = Product.objects.create(
            name='Product B',
            code='PROD-B',
            category=self.category,
            department=self.dept_b,
            quantity=0,
            min_stock=5,
        )

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a',
            password='Password123!',
            role='encargado',
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            password='Password123!',
            role='encargado',
            department=self.dept_b,
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='Password123!',
            role='admin',
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type='sin_stock',
            message='Stock depleted for Product A',
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type='sin_stock',
            message='Stock depleted for Product B',
            is_read=False,
        )

    def test_encargado_cannot_mark_alert_of_other_dept_as_read(self):
        """
        Verify that a non-admin cannot mark another department's alert as read.
        Should return 404 and leave is_read unchanged.
        """
        self.client.login(username='user_a', password='Password123!')
        url = reverse(
            'alertas:alert_mark_read',
            kwargs={'pk': self.alert_b.pk},
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_dept_alert_as_read(self):
        """Verify that a non-admin can mark their own dept alert as read."""
        self.client.login(username='user_a', password='Password123!')
        url = reverse(
            'alertas:alert_mark_read',
            kwargs={'pk': self.alert_a.pk},
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify that an admin can mark any department alert as read."""
        self.client.login(username='admin_user', password='Password123!')
        url = reverse(
            'alertas:alert_mark_read',
            kwargs={'pk': self.alert_b.pk},
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
