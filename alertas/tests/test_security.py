from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert

class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name="Dept A", code="A")
        self.dept_b = Department.objects.create(name="Dept B", code="B")

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
        self.admin = User.objects.create_superuser(
            username="admin",
            password="password123",
            role="admin",
            email="admin@example.com"
        )

        # Create category
        self.category = Category.objects.create(name="Cat 1")

        # Create products
        self.prod_a = Product.objects.create(
            name="Prod A",
            code="CODEA",
            category=self.category,
            department=self.dept_a,
            quantity=10,
            min_stock=5
        )
        self.prod_b = Product.objects.create(
            name="Prod B",
            code="CODEB",
            category=self.category,
            department=self.dept_b,
            quantity=10,
            min_stock=5
        )

        # Create alerts
        self.alert_a = Alert.objects.create(
            product=self.prod_a,
            alert_type="stock_bajo",
            message="Stock bajo para Prod A"
        )
        self.alert_b = Alert.objects.create(
            product=self.prod_b,
            alert_type="stock_bajo",
            message="Stock bajo para Prod B"
        )

        # Create clients
        self.client_a = Client()
        self.client_a.login(username="user_a", password="password123")

        self.client_b = Client()
        self.client_b.login(username="user_b", password="password123")

        self.client_admin = Client()
        self.client_admin.login(username="admin", password="password123")

    def test_non_admin_cannot_mark_other_dept_alert_as_read(self):
        # user_a (Dept A) tries to mark alert_b (Dept B) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client_a.post(url)

        # Should return 404
        self.assertEqual(response.status_code, 404)

        # Verify alert_b is still unread
        self.alert_b.refresh_from_db()
        self.assertFalse(self.alert_b.is_read)

    def test_non_admin_can_mark_own_dept_alert_as_read(self):
        # user_a (Dept A) marks alert_a (Dept A) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client_a.post(url)

        # Should redirect to list
        self.assertEqual(response.status_code, 302)

        # Verify alert_a is now read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)

    def test_admin_can_mark_any_dept_alert_as_read(self):
        # admin marks alert_a (Dept A) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_a.pk})
        response = self.client_admin.post(url)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Verify alert_a is read
        self.alert_a.refresh_from_db()
        self.assertTrue(self.alert_a.is_read)
