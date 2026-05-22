from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertasSecurityTests(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name='Dept 1', code='D1')
        self.dept2 = Department.objects.create(name='Dept 2', code='D2')

        # Create users
        self.user_dept1 = User.objects.create_user(
            username='user1', password='password', department=self.dept1, role='encargado'
        )
        self.user_dept2 = User.objects.create_user(
            username='user2', password='password', department=self.dept2, role='encargado'
        )

        # Create categories
        self.cat = Category.objects.create(name='Cat 1')

        # Create products
        self.prod1 = Product.objects.create(
            name='Prod 1', code='P1', department=self.dept1, category=self.cat, quantity=10, min_stock=5
        )
        self.prod2 = Product.objects.create(
            name='Prod 2', code='P2', department=self.dept2, category=self.cat, quantity=10, min_stock=5
        )

        # Create alerts
        self.alert1 = Alert.objects.create(
            product=self.prod1, alert_type='stock_bajo', message='Bajo stock P1'
        )
        self.alert2 = Alert.objects.create(
            product=self.prod2, alert_type='stock_bajo', message='Bajo stock P2'
        )

        self.client = Client()

    def test_idor_mark_read_other_department(self):
        """
        Test that a user cannot mark an alert from another department as read.
        """
        self.client.login(username='user1', password='password')

        # user1 (Dept 1) tries to mark alert2 (Dept 2) as read
        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})
        response = self.client.post(url)

        # It should return 404 if the fix is in place, but currently it likely returns 302 (redirect)
        # because AlertMarkReadView doesn't filter the queryset.
        self.alert2.refresh_from_db()

        # If vulnerable, this will be True
        self.assertFalse(self.alert2.is_read, "User marked an alert from another department as read!")
