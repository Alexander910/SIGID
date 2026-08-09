from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404

from usuarios.models import Department, User
from inventario.models import Category, Product
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        # Create departments
        self.dept_sistemas = Department.objects.create(name='Sistemas', code='SIS')
        self.dept_ventas = Department.objects.create(name='Ventas', code='VEN')

        # Create category
        self.category = Category.objects.create(name='Equipos')

        # Create products
        self.product_sis = Product.objects.create(
            name='Laptop',
            code='LAP01',
            category=self.category,
            department=self.dept_sistemas,
            quantity=10,
            min_stock=5
        )
        self.product_ven = Product.objects.create(
            name='Impresora',
            code='IMP01',
            category=self.category,
            department=self.dept_ventas,
            quantity=8,
            min_stock=4
        )

        # Create alerts
        self.alert_sis = Alert.objects.create(
            product=self.product_sis,
            alert_type='stock_bajo',
            message='Stock bajo para Laptop',
            is_read=False
        )
        self.alert_ven = Alert.objects.create(
            product=self.product_ven,
            alert_type='stock_bajo',
            message='Stock bajo para Impresora',
            is_read=False
        )

        # Create users
        self.user_sistemas = User.objects.create_user(
            username='user_sis',
            password='password123',
            role='encargado',
            department=self.dept_sistemas
        )
        self.admin_user = User.objects.create_user(
            username='user_admin',
            password='password123',
            role='admin'
        )

    def test_encargado_can_mark_own_department_alert_read(self):
        """Test that an encargado can mark an alert belonging to their own department as read."""
        self.client.login(username='user_sis', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_sis.pk})
        response = self.client.post(url)

        # Verify redirect
        self.assertEqual(response.status_code, 302)

        # Refresh from DB and verify is_read is True
        self.alert_sis.refresh_from_db()
        self.assertTrue(self.alert_sis.is_read)

    def test_encargado_cannot_mark_other_department_alert_read(self):
        """Test that an encargado cannot mark an alert from another department as read (receives 404)."""
        self.client.login(username='user_sis', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_ven.pk})
        response = self.client.post(url)

        # Verify 404 Not Found due to get_object_or_404 filtering
        self.assertEqual(response.status_code, 404)

        # Verify alert is still unread in database
        self.alert_ven.refresh_from_db()
        self.assertFalse(self.alert_ven.is_read)

    def test_admin_can_mark_any_alert_read(self):
        """Test that an admin can mark an alert from any department as read."""
        self.client.login(username='user_admin', password='password123')

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_ven.pk})
        response = self.client.post(url)

        # Verify redirect
        self.assertEqual(response.status_code, 302)

        # Refresh from DB and verify is_read is True
        self.alert_ven.refresh_from_db()
        self.assertTrue(self.alert_ven.is_read)
