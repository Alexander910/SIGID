from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user1 = User.objects.create_user(
            username='user1', password='password123',
            department=self.dept1, role='encargado'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password123',
            department=self.dept2, role='encargado'
        )

        self.category = Category.objects.create(name='Cat 1')
        self.product1 = Product.objects.create(
            name='Product 1', code='P1', category=self.category,
            department=self.dept1, quantity=10, min_stock=5
        )

        self.alert1 = Alert.objects.create(
            product=self.product1, alert_type='stock_bajo', message='Bajo stock'
        )

    def test_idor_alert_mark_read(self):
        """Test that a user cannot mark as read an alert from another department."""
        self.client.login(username='user2', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert1.pk})

        # User 2 is from Dept 2, Alert 1 is from Dept 1.
        # This SHOULD return 404 if fixed, but currently likely returns 302 (redirect)
        response = self.client.post(url)

        # Check if the alert was marked as read anyway (Vulnerability check)
        self.alert1.refresh_from_db()

        if response.status_code == 302 and self.alert1.is_read:
            self.fail("IDOR Vulnerability: User2 marked Alert1 as read even though they belong to different departments.")

        self.assertEqual(response.status_code, 404)
