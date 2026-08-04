from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Category, Product
from alertas.models import Alert

User = get_user_model()


class AlertSecurityTestCase(TestCase):
    """Pruebas de seguridad para verificar protección contra IDOR en alertas."""

    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Department A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Department B", code="DEPTB")

        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )

        self.encargado_a = User.objects.create_user(
            username="encargado_a",
            email="a@example.com",
            password="password_a",
            role="encargado",
            department=self.dept_a
        )
        self.encargado_b = User.objects.create_user(
            username="encargado_b",
            email="b@example.com",
            password="password_b",
            role="encargado",
            department=self.dept_b
        )

        # Create Category
        self.category = Category.objects.create(name="General")

        # Create Products
        self.product_a = Product.objects.create(
            name="Product A",
            code="PA",
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PB",
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Create Alerts
        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="stock_bajo",
            message="Stock bajo para Product A"
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Stock bajo para Product B"
        )

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """Verify IDOR protection: non-admin from Dept A cannot mark Dept B's alert as read."""
        self.client.login(username="encargado_a", password="password_a")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        # This request should return 404 (Not Found)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Check that alert state in database remains unread (is_read=False)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Non-admin from Dept A can mark Dept A's alert as read."""
        self.client.login(username="encargado_a", password="password_a")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        # Check that alert state has been updated to is_read=True
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        """Admin user can mark any department's alert as read."""
        self.client.login(username="admin", password="adminpassword")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        # Check that alert state has been updated to is_read=True
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
