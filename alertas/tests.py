from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertasSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.admin = User.objects.create_user(username="admin", password="password", role="admin")
        self.user1 = User.objects.create_user(username="user1", password="password", role="encargado", department=self.dept1)
        self.user2 = User.objects.create_user(username="user2", password="password", role="encargado", department=self.dept2)

        self.cat = Category.objects.create(name="Cat")
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10, min_stock=5)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", category=self.cat, department=self.dept2, quantity=10, min_stock=5)

        self.alert1 = Alert.objects.create(product=self.prod1, alert_type="stock_bajo", message="Bajo stock P1")
        self.alert2 = Alert.objects.create(product=self.prod2, alert_type="stock_bajo", message="Bajo stock P2")

    def test_idor_mark_read(self):
        """Test that user1 cannot mark user2's alert as read."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_idor_mark_all_read_safe(self):
        """Verify that AlertMarkAllReadView only marks own alerts as read."""
        self.client.login(username="user1", password="password")
        url = reverse('alertas:alert_mark_all_read')
        response = self.client.post(url)

        self.alert1.refresh_from_db()
        self.alert2.refresh_from_db()

        self.assertTrue(self.alert1.is_read)
        self.assertFalse(self.alert2.is_read)
