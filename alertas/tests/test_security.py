from django.test import TestCase, Client
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Dept A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Dept B", code="DEPTB")

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
            message="Alert A",
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Alert B",
            is_read=False
        )

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

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """Verify that an 'encargado' user from Department A cannot mark an alert from Department B as read."""
        self.client.force_login(self.user_a)

        # Try to mark alert_b (Department B) as read
        from django.urls import reverse
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})

        response = self.client.post(url)

        # Verify 404 status (unauthorized access attempt)
        self.assertEqual(response.status_code, 404)

        # Verify database state remains unchanged
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """Verify that an 'encargado' user from Department A can mark an alert from Department A as read."""
        self.client.force_login(self.user_a)

        from django.urls import reverse
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        response = self.client.post(url)

        # Verify 302 redirect
        self.assertEqual(response.status_code, 302)

        # Verify database state updated successfully
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Verify that an admin user can mark any alert from any department as read."""
        self.client.force_login(self.admin_user)

        from django.urls import reverse
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)
