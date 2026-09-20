from django.test import TestCase
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


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
            department=self.dept_a,
        )
        self.user_b = User.objects.create_user(
            username="user_b",
            password="password123",
            role="encargado",
            department=self.dept_b,
        )
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            password="password123",
            role="admin",
        )

        # Create products and alerts
        self.category = Category.objects.create(name="General")
        self.product_a = Product.objects.create(
            name="Product A",
            code="PROD_A",
            department=self.dept_a,
            category=self.category,
            quantity=0,
            min_stock=5,
        )
        self.product_b = Product.objects.create(
            name="Product B",
            code="PROD_B",
            department=self.dept_b,
            category=self.category,
            quantity=0,
            min_stock=5,
        )

        self.alert_a = Alert.objects.create(
            product=self.product_a,
            alert_type="sin_stock",
            message="Alert A",
            is_read=False,
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b,
            alert_type="sin_stock",
            message="Alert B",
            is_read=False,
        )

    def test_idor_prevent_user_marking_other_department_alert_read(self):
        # User A logs in
        self.client.login(username="user_a", password="password123")

        # User A tries to mark Alert B (belonging to Dept B) as read
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        # Should return 404
        self.assertEqual(response.status_code, 404)

        # Verify Alert B is still unread in DB
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_user_can_mark_own_department_alert_read(self):
        # User A logs in
        self.client.login(username="user_a", password="password123")

        # User A marks Alert A as read
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_a.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_alert_read(self):
        # Admin logs in
        self.client.login(username="admin_user", password="password123")

        # Admin marks Alert B as read
        url = reverse("alertas:alert_mark_read", kwargs={"pk": self.alert_b.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_b.refresh_from_db()
        self.assertTrue(self.alert_b.is_read)
