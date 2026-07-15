from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", department=self.dept1, role="encargado")
        self.user2 = User.objects.create_user(username="user2", password="password", department=self.dept2, role="encargado")

        self.cat = Category.objects.create(name="Cat")
        self.prod1 = Product.objects.create(name="Prod 1", code="P1", department=self.dept1, category=self.cat)
        self.prod2 = Product.objects.create(name="Prod 2", code="P2", department=self.dept2, category=self.cat)

        self.alert1 = Alert.objects.create(product=self.prod1, message="Alert 1")
        self.alert2 = Alert.objects.create(product=self.prod2, message="Alert 2")

        self.client1 = Client()
        self.client1.login(username="user1", password="password")

    def test_idor_mark_read(self):
        # User 1 should NOT be able to mark alert 2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client1.post(url)

        # Current implementation probably returns 302 because it redirects after saving
        # but it SHOULD return 404 if it's properly secured.

        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read, "User1 should NOT be able to mark Alert2 as read")

    def test_admin_can_mark_any_read(self):
        # Admin should be able to mark any alert as read
        admin = User.objects.create_superuser(username="admin", password="password", role="admin")
        self.client.login(username="admin", password="password")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)

    def test_user_can_mark_own_dept_read(self):
        # User 1 should be able to mark alert 1 (Dept 1) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client1.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)
