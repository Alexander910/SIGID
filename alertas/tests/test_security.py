from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Create users
        self.user_encargado1 = User.objects.create_user(
            username='encargado1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.user_encargado2 = User.objects.create_user(
            username='encargado2',
            password='password123',
            role='encargado',
            department=self.dept2
        )
        self.user_admin = User.objects.create_user(
            username='adminuser',
            password='password123',
            role='admin'
        )

        # Create categories & products
        self.cat = Category.objects.create(name='General')
        self.product1 = Product.objects.create(
            name='Prod 1',
            code='P1',
            category=self.cat,
            department=self.dept1,
            quantity=0,
            min_stock=5
        )
        self.product2 = Product.objects.create(
            name='Prod 2',
            code='P2',
            category=self.cat,
            department=self.dept2,
            quantity=0,
            min_stock=5
        )

        # Create alerts
        self.alert_dept1 = Alert.objects.create(
            product=self.product1,
            alert_type='sin_stock',
            message='Sin stock'
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.product2,
            alert_type='sin_stock',
            message='Sin stock'
        )

    def test_encargado_cannot_mark_read_other_dept_alert(self):
        """Encargado from Dept 1 should receive 404 when marking Dept 2 alert as read."""
        self.client.login(username='encargado1', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_dept2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Verify DB state unchanged
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_encargado_can_mark_read_own_dept_alert(self):
        """Encargado from Dept 1 can mark Dept 1 alert as read."""
        self.client.login(username='encargado1', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_dept1.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify DB state updated
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_read_any_alert(self):
        """Admin can mark alerts from any department as read."""
        self.client.login(username='adminuser', password='password123')
        url = reverse('alertas:alert_mark_read', args=[self.alert_dept2.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        # Verify DB state updated
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
