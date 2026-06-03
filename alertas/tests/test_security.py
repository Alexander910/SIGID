from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(
            username="user1",
            password="password",
            role="encargado",
            department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="password",
            role="encargado",
            department=self.dept2
        )

        self.cat = Category.objects.create(name="Cat 1")

        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.cat,
            department=self.dept1, quantity=10, min_stock=5
        )
        self.prod2 = Product.objects.create(
            name="Prod 2", code="P2", category=self.cat,
            department=self.dept2, quantity=10, min_stock=5
        )

        self.alert1 = Alert.objects.create(
            product=self.prod1, alert_type="stock_bajo", message="Low stock"
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2, alert_type="stock_bajo", message="Low stock"
        )

    def test_encargado_cannot_mark_alert_from_other_department_as_read(self):
        """
        Verify that a user (encargado) cannot mark an alert as read
         if the product belongs to a different department.
        """
        self.client.login(username="user1", password="password")

        # User 1 (Dept 1) tries to mark Alert 2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # Should return 404 if filtered correctly, or we could expect a 403
        # but the common way to fix IDOR in Django is filtering the queryset which results in 404.
        self.assertEqual(response.status_code, 404)

        # Verify alert is still unread
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_encargado_can_mark_own_department_alert_as_read(self):
        """
        Verify that a user can mark their own department's alerts as read.
        """
        self.client.login(username="user1", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302) # Redirects to list
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
