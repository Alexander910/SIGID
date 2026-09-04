from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="IT", code="DEP_IT")
        self.dept2 = Department.objects.create(name="HR", code="DEP_HR")

        # Create users
        self.user_dept1 = User.objects.create_user(
            username="user_it",
            password="password123",
            role="encargado",
            department=self.dept1
        )
        self.user_dept2 = User.objects.create_user(
            username="user_hr",
            password="password123",
            role="encargado",
            department=self.dept2
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="password123",
            role="admin"
        )

        # Create products
        self.prod_dept1 = Product.objects.create(
            name="Laptop IT",
            code="LAP01",
            department=self.dept1,
            quantity=0,
            min_stock=5
        )
        self.prod_dept2 = Product.objects.create(
            name="Desk HR",
            code="DSK01",
            department=self.dept2,
            quantity=0,
            min_stock=5
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.prod_dept1,
            alert_type="sin_stock",
            message="No stock for Laptop IT"
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.prod_dept2,
            alert_type="sin_stock",
            message="No stock for Desk HR"
        )

        self.client = Client()

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """User from dept1 attempting to mark dept2 alert as read should receive 404."""
        self.client.login(username="user_it", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

        # Verify alert remained unread
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User from dept1 marking dept1 alert as read should succeed."""
        self.client.login(username="user_it", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert is marked as read
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin user can mark alert from any department as read."""
        self.client.login(username="admin_user", password="password123")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Verify alert is marked as read
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
