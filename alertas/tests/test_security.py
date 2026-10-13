import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Category, Product
from alertas.models import Alert

User = get_user_model()


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Department A", code="DEPT_A")
        self.dept_b = Department.objects.create(name="Department B", code="DEPT_B")

        # Create users
        self.user_a = User.objects.create_user(
            username="user_a",
            password="password123",
            role="encargado",
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            password="password123",
            role="encargado",
            department=self.dept_b
        )
        self.admin = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin"
        )

        # Create category
        self.category = Category.objects.create(
            name="General Category",
            description="General"
        )

        # Create products
        self.prod_a = Product.objects.create(
            name="Product A",
            code="PRODA",
            category=self.category,
            department=self.dept_a,
            quantity=5,
            min_stock=10
        )
        self.prod_b = Product.objects.create(
            name="Product B",
            code="PRODB",
            category=self.category,
            department=self.dept_b,
            quantity=2,
            min_stock=10
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type="stock_bajo",
            message="Low stock for product A",
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type="stock_bajo",
            message="Low stock for product B",
            is_read=False
        )

        self.client = Client()

    def test_idor_prevent_user_marking_other_dept_alert_as_read(self):
        """User A should not be able to mark Alert B (Dept B) as read."""
        self.client.login(username="user_a", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)

        # Should return 404 because user_a's queryset is scoped to dept_a
        self.assertEqual(response.status_code, 404)

        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_dept_alert_as_read(self):
        """User A can mark Alert A (Dept A) as read."""
        self.client.login(username="user_a", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin can mark Alert B (Dept B) as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
