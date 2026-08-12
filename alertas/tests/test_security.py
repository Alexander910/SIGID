from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Department
from inventario.models import Category, Product
from alertas.models import Alert

User = get_user_model()

class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Department A", code="DEPTA")
        self.dept_b = Department.objects.create(name="Department B", code="DEPTB")

        # Create category
        self.category = Category.objects.create(name="General")

        # Create products for each department
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
            message="Stock is low on A",
            is_read=False
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="stock_bajo",
            message="Stock is low on B",
            is_read=False
        )

        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        # Note: save() automatically sets role='admin' for superuser,
        # but let's be explicit and ensure role is 'admin' for safety.
        self.admin_user.role = 'admin'
        self.admin_user.save()

        self.user_a = User.objects.create_user(
            username="user_a",
            email="usera@example.com",
            password="userpassword",
            role="encargado",
            department=self.dept_a
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            email="userb@example.com",
            password="userpassword",
            role="encargado",
            department=self.dept_b
        )
        self.user_no_dept = User.objects.create_user(
            username="user_no_dept",
            email="usernodept@example.com",
            password="userpassword",
            role="encargado",
            department=None
        )

    def test_admin_can_mark_any_alert_as_read(self):
        self.client.login(username="admin", password="adminpassword")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302) # Redirects to alert list
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        self.client.login(username="user_a", password="userpassword")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_user_cannot_mark_other_department_alert_as_read_idor(self):
        # user_a attempts to mark alert_b (Department B) as read
        self.client.login(username="user_a", password="userpassword")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # Security Preference: verify that unauthorized access attempts receive an explicit 404 status
        self.assertEqual(response.status_code, 404)

        # Database state remains unchanged
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_without_department_cannot_mark_any_alert_as_read(self):
        # user_no_dept attempts to mark alert_a
        self.client.login(username="user_no_dept", password="userpassword")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_a.refresh_from_db()
        self.assertFalse(self.alert_a.is_read)
