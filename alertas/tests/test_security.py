from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Department, User
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept_a = Department.objects.create(name='Dept A', code='A')
        self.dept_b = Department.objects.create(name='Dept B', code='B')

        # Create users
        self.user_a = User.objects.create_user(
            username='user_a', password='password123', department=self.dept_a, role='encargado'
        )
        self.user_b = User.objects.create_user(
            username='user_b', password='password123', department=self.dept_b, role='encargado'
        )

        # Create category
        self.category = Category.objects.create(name='General')

        # Create product and alert for Dept B
        self.product_b = Product.objects.create(
            name='Product B', code='PB', category=self.category, department=self.dept_b, quantity=0
        )
        self.alert_b = Alert.objects.create(
            product=self.product_b, alert_type='sin_stock', message='Out of stock'
        )

    def test_idor_alert_mark_read(self):
        """
        Verify that a user from Dept A cannot mark an alert from Dept B as read.
        """
        self.client.login(username='user_a', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_b.pk})
        response = self.client.post(url)

        # In the vulnerable version, this will redirect (302) and mark as read
        # In the secure version, it should return 404

        self.alert_b.refresh_from_db()

        # This assertion should FAIL in the vulnerable version
        self.assertFalse(self.alert_b.is_read, "User A was able to mark User B's alert as read!")
        if response.status_code == 302:
             # If it redirected, it likely succeeded (vulnerable)
             pass
