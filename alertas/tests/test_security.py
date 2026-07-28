from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Dept A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Dept B", code="DEPTB")

        # Create users
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        # Ensure admin role is set
        self.admin.role = 'admin'
        self.admin.save()

        self.user_a = User.objects.create_user(
            username="user_a", email="usera@example.com", password="password",
            role="encargado", department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="user_b", email="userb@example.com", password="password",
            role="encargado", department=self.dept_b
        )

        # Create category
        self.cat = Category.objects.create(name="Cat 1")

        # Create products
        self.prod_a = Product.objects.create(
            name="Product A", code="PRODA", category=self.cat, department=self.dept_a, quantity=10, min_stock=5
        )
        self.prod_b = Product.objects.create(
            name="Product B", code="PRODB", category=self.cat, department=self.dept_b, quantity=10, min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a, alert_type="stock_bajo", message="Stock low A", is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b, alert_type="stock_bajo", message="Stock low B", is_read=False
        )

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username="admin", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_authorized_user_can_mark_their_department_alert_as_read(self):
        self.client.login(username="user_a", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_unauthorized_user_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username="user_a", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)
