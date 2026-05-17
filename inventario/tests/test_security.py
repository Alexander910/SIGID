from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product
from alertas.models import Alert

class SecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(
            username="user1", password="password123",
            role="encargado", department=self.dept1
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password123",
            role="encargado", department=self.dept2
        )

        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", department=self.dept1, quantity=10
        )
        self.prod2 = Product.objects.create(
            name="Prod 2", code="P2", department=self.dept2, quantity=20
        )

        self.client = Client()

    def test_unauthorized_access_to_other_department_product(self):
        self.client.login(username="user1", password="password123")

        # User 1 should NOT be able to see Product 2 (Dept 2)
        response = self.client.get(reverse('inventario:product_update', kwargs={'pk': self.prod2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_department_assignment_on_creation(self):
        self.client.login(username="user1", password="password123")

        # User 1 tries to create a product for Dept 2
        response = self.client.post(reverse('inventario:product_create'), {
            'name': 'Malicious Product',
            'code': 'MAL1',
            'department': self.dept2.id,
            'quantity': 5,
            'min_stock': 1
        })

        # The product should be created but assigned to User 1's department (Dept 1)
        # OR it should fail validation.
        # Looking at ProductCreateView.form_valid, it forces form.instance.department = self.request.user.department

        product = Product.objects.get(code='MAL1')
        self.assertEqual(product.department, self.dept1)

    def test_unauthorized_product_assignment_on_movement_creation(self):
        self.client.login(username="user1", password="password123")

        # User 1 tries to create a movement for Product 2 (Dept 2)
        response = self.client.post(reverse('movimientos:movement_create'), {
            'product': self.prod2.id,
            'type': 'entrada',
            'quantity': 5,
            'observation': 'Stealing stock'
        })

        # The form should fail validation because Product 2 is not in the queryset
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('product', response.context['form'].errors)

    def test_unauthorized_alert_mark_read(self):
        alert2 = Alert.objects.create(
            product=self.prod2,
            alert_type='stock_bajo',
            message='Stock is low'
        )

        self.client.login(username="user1", password="password123")

        # User 1 tries to mark Alert 2 (Dept 2) as read
        response = self.client.post(reverse('alertas:alert_mark_read', kwargs={'pk': alert2.pk}))

        # Should now return 404
        self.assertEqual(response.status_code, 404)

        alert2.refresh_from_db()
        self.assertFalse(alert2.is_read)
