from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(
            username='user1', password='password123', role='encargado', department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password123', role='encargado', department=self.dept2
        )
        self.admin = User.objects.create_user(
            username='adminuser', password='password123', role='admin', department=None
        )

        self.category = Category.objects.create(name='Cat 1', description='Cat desc')

        self.product1 = Product.objects.create(
            name='Prod 1', code='P1', category=self.category, department=self.dept1, quantity=0, min_stock=5
        )
        self.product2 = Product.objects.create(
            name='Prod 2', code='P2', category=self.category, department=self.dept2, quantity=0, min_stock=5
        )

        self.alert1 = Alert.objects.create(
            product=self.product1, alert_type='sin_stock', message='Out of stock 1', is_read=False
        )
        self.alert2 = Alert.objects.create(
            product=self.product2, alert_type='sin_stock', message='Out of stock 2', is_read=False
        )

    def test_user_cannot_mark_other_department_alert_as_read(self):
        """Verify IDOR protection: User 1 cannot mark alert belonging to Dept 2 as read."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert2.refresh_from_db()
        self.assertFalse(self.alert2.is_read)

    def test_user_can_mark_own_department_alert_as_read(self):
        """User 1 can mark alert belonging to Dept 1 as read."""
        self.client.login(username='user1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert1.refresh_from_db()
        self.assertTrue(self.alert1.is_read)

    def test_admin_can_mark_any_alert_as_read(self):
        """Admin can mark alerts from any department as read."""
        self.client.login(username='adminuser', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert2.refresh_from_db()
        self.assertTrue(self.alert2.is_read)
