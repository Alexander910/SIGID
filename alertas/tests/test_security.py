from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Product, Category
from alertas.models import Alert

User = get_user_model()

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_it = Department.objects.create(name="IT Department", code="IT")
        self.dept_hr = Department.objects.create(name="HR Department", code="HR")

        # Create users
        self.user_it = User.objects.create_user(
            username="user_it", password="password123", role="encargado", department=self.dept_it
        )
        self.user_hr = User.objects.create_user(
            username="user_hr", password="password123", role="encargado", department=self.dept_hr
        )
        self.admin = User.objects.create_user(
            username="admin", password="password123", role="admin"
        )

        # Create category
        self.category = Category.objects.create(name="Electronics")

        # Create products
        self.product_it = Product.objects.create(
            name="Laptop", code="IT-01", department=self.dept_it, category=self.category, quantity=10
        )
        self.product_hr = Product.objects.create(
            name="HR Manual", code="HR-01", department=self.dept_hr, category=self.category, quantity=5
        )

        # Create alerts
        self.alert_it = Alert.objects.create(
            product=self.product_it, alert_type="stock_bajo", message="Low stock on IT Laptop", is_read=False
        )
        self.alert_hr = Alert.objects.create(
            product=self.product_hr, alert_type="stock_bajo", message="Low stock on HR Manual", is_read=False
        )

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """
        Verify that a non-admin user (encargado) receives a 404 response
        and the alert's is_read status remains False when attempting to mark
        an alert belonging to another department as read (IDOR prevention).
        """
        self.client.login(username="user_it", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_hr.pk})

        response = self.client.post(url)

        # Verify unauthorized access attempts receive an explicit 404 status
        self.assertEqual(response.status_code, 404)

        # Verify database state remains unchanged
        self.alert_hr.refresh_from_db()
        self.assertFalse(self.alert_hr.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """
        Verify that a non-admin user (encargado) can successfully mark
        an alert from their own department as read.
        """
        self.client.login(username="user_it", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_it.pk})

        response = self.client.post(url)

        # Verify successful redirect after marking as read
        self.assertEqual(response.status_code, 302)

        # Verify alert status is updated in the database
        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """
        Verify that an administrator retains full access and can mark any
        alert from any department as read.
        """
        self.client.login(username="admin", password="password123")
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_hr.pk})

        response = self.client.post(url)

        # Verify admin gets redirected
        self.assertEqual(response.status_code, 302)

        # Verify alert is marked as read
        self.alert_hr.refresh_from_db()
        self.assertTrue(self.alert_hr.is_read)
