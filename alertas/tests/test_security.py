from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Dept A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Dept B", code="DEPTB")

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
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin"
        )

        # Create category
        self.category = Category.objects.create(name="General Category")

        # Create products
        self.product_a = Product.objects.create(
            name="Product A",
            code="PRODA",
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PRODB",
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Stock is low for Product A"
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Stock is low for Product B"
        )

    def test_authorized_user_can_mark_alert_read(self):
        """User from Dept A can mark their own alert as read."""
        self.client.force_login(self.user_a)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify alert is indeed marked as read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_unauthorized_user_cannot_mark_other_dept_alert_read(self):
        """User from Dept A cannot mark Dept B alert as read (IDOR prevention)."""
        self.client.force_login(self.user_a)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verify alert is NOT marked as read
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Admin can mark any alert as read regardless of department."""
        self.client.force_login(self.admin_user)
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify alert is indeed marked as read
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_anonymous_user_is_redirected(self):
        """Anonymous user cannot mark alerts as read."""
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        # Should redirect to login
        self.assertIn('/login/', response.url)

        # Verify alert is NOT marked as read
        self.alert_a.refresh_from_db()
        self.assertFalse(self.alert_a.is_read)
