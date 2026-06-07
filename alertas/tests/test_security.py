from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category
from alertas.models import Alert

class AlertSecurityTest(TestCase):
    def setUp(self):
        # Create departments
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        # Create users
        self.user1 = User.objects.create_user(
            username="user1",
            password="password123",
            department=self.dept1,
            role='encargado'
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="password123",
            department=self.dept2,
            role='encargado'
        )

        # Create category
        self.cat = Category.objects.create(name="Cat 1")

        # Create product in dept 2
        self.prod2 = Product.objects.create(
            name="Prod 2",
            code="P2",
            category=self.cat,
            department=self.dept2,
            quantity=0
        )

        # Create alert for product in dept 2
        self.alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type='sin_stock',
            message="No stock"
        )

        self.client = Client()

    def test_unauthorized_mark_read_idor(self):
        """
        Verify that a user from Dept 1 cannot mark as read an alert from Dept 2.
        """
        self.client.login(username="user1", password="password123")

        url = reverse('alertas:alert_mark_read', kwargs={'pk': self.alert2.pk})

        # Currently, this should FAIL the security requirement (it will succeed in marking it read)
        # We want it to eventually return 404.
        response = self.client.post(url)

        # Check if the alert is now read (it shouldn't be if secured)
        self.alert2.refresh_from_db()

        # If the vulnerability exists, is_read will be True and response will be redirect (302)
        # If fixed, it should be 404 and is_read should be False.
        self.assertFalse(self.alert2.is_read, "User should NOT be able to mark alert from another department as read")
