from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert


class AlertSecurityTestCase(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        self.user_encargado_dept1 = User.objects.create_user(
            username='user_dept1',
            password='password123',
            role='encargado',
            department=self.dept1
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='password123',
            role='admin'
        )

        self.category = Category.objects.create(name='General')

        self.prod_dept1 = Product.objects.create(
            name='Prod 1',
            code='P1',
            category=self.category,
            department=self.dept1,
            quantity=5,
            min_stock=10
        )
        self.prod_dept2 = Product.objects.create(
            name='Prod 2',
            code='P2',
            category=self.category,
            department=self.dept2,
            quantity=5,
            min_stock=10
        )

        self.alert_dept1 = Alert.objects.create(
            product=self.prod_dept1,
            alert_type='stock_bajo',
            message='Stock bajo en Prod 1'
        )
        self.alert_dept2 = Alert.objects.create(
            product=self.prod_dept2,
            alert_type='stock_bajo',
            message='Stock bajo en Prod 2'
        )

    def test_encargado_cannot_mark_read_alert_from_other_department(self):
        """A non-admin user should get 404 when marking an alert from another department as read (IDOR prevention)."""
        self.client.login(username='user_dept1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.alert_dept2.refresh_from_db()
        self.assertFalse(self.alert_dept2.is_read)

    def test_encargado_can_mark_read_own_department_alert(self):
        """A non-admin user should successfully mark an alert from their own department as read."""
        self.client.login(username='user_dept1', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept1.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept1.refresh_from_db()
        self.assertTrue(self.alert_dept1.is_read)

    def test_admin_can_mark_read_any_department_alert(self):
        """An admin user should be able to mark alerts from any department as read."""
        self.client.login(username='admin_user', password='password123')
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert_dept2.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.alert_dept2.refresh_from_db()
        self.assertTrue(self.alert_dept2.is_read)
