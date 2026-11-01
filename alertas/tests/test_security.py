from django.test import TestCase
from django.urls import reverse
from alertas.models import Alert
from inventario.models import Category, Product
from usuarios.models import Department, User


class AlertSecurityTests(TestCase):
    """Test suite for checking IDOR protection in Alert views."""

    def setUp(self):
        # Create departments
        self.dept_it = Department.objects.create(
            name='IT Department',
            code='IT',
        )
        self.dept_hr = Department.objects.create(
            name='HR Department',
            code='HR',
        )

        # Create category
        self.category = Category.objects.create(
            name='General Supplies',
            description='Supplies category',
        )

        # Create products
        self.product_it = Product.objects.create(
            name='Laptop',
            code='LAP01',
            category=self.category,
            department=self.dept_it,
            quantity=1,
            min_stock=5,
        )
        self.product_hr = Product.objects.create(
            name='Desk Chair',
            code='CHR01',
            category=self.category,
            department=self.dept_hr,
            quantity=0,
            min_stock=2,
        )

        # Create alerts
        self.alert_it = Alert.objects.create(
            product=self.product_it,
            alert_type='stock_bajo',
            message='Stock bajo para Laptop',
            is_read=False,
        )
        self.alert_hr = Alert.objects.create(
            product=self.product_hr,
            alert_type='sin_stock',
            message='Sin stock para Desk Chair',
            is_read=False,
        )

        # Create users
        self.user_it = User.objects.create_user(
            username='encargado_it',
            password='Password123!',
            role='encargado',
            department=self.dept_it,
        )
        self.user_hr = User.objects.create_user(
            username='encargado_hr',
            password='Password123!',
            role='encargado',
            department=self.dept_hr,
        )
        self.admin = User.objects.create_user(
            username='admin_user',
            password='Password123!',
            role='admin',
            department=self.dept_it,
        )

    def test_encargado_can_mark_own_department_alert_as_read(self):
        self.client.login(username='encargado_it', password='Password123!')
        url = reverse('alertas:alert_mark_read', args=[self.alert_it.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert_it.refresh_from_db()
        self.assertTrue(self.alert_it.is_read)

    def test_encargado_cannot_mark_other_department_alert_as_read(self):
        self.client.login(username='encargado_it', password='Password123!')
        url = reverse('alertas:alert_mark_read', args=[self.alert_hr.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.alert_hr.refresh_from_db()
        self.assertFalse(self.alert_hr.is_read)

    def test_admin_can_mark_any_department_alert_as_read(self):
        self.client.login(username='admin_user', password='Password123!')
        url = reverse('alertas:alert_mark_read', args=[self.alert_hr.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('alertas:alert_list'))

        self.alert_hr.refresh_from_db()
        self.assertTrue(self.alert_hr.is_read)
