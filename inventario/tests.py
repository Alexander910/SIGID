from django.test import TestCase
from django.urls import reverse
from usuarios.models import User, Department
from inventario.models import Product, Category

class ProductSecurityTest(TestCase):
    def setUp(self):
        self.dept1 = Department.objects.create(name="Dept 1", code="D1")
        self.dept2 = Department.objects.create(name="Dept 2", code="D2")

        self.user1 = User.objects.create_user(username="user1", password="password", role="encargado", department=self.dept1)

        self.cat = Category.objects.create(name="Cat")
        self.prod1 = Product.objects.create(
            name="Prod 1", code="P1", category=self.cat, department=self.dept1, quantity=10, min_stock=5
        )

    def test_department_tampering_protection(self):
        """Test that user1 cannot change a product's department via POST."""
        self.client.login(username="user1", password="password")
        url = reverse('inventario:product_update', kwargs={'pk': self.prod1.pk})

        # Attempt to change department to dept2
        data = {
            'name': 'Prod 1 Updated',
            'code': 'P1',
            'category': self.cat.pk,
            'department': self.dept2.pk, # Tampered
            'quantity': 10,
            'min_stock': 5,
        }

        response = self.client.post(url, data)

        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.name, 'Prod 1 Updated')
        self.assertEqual(self.prod1.department, self.dept1) # Should NOT have changed to dept2
        print(f"\nDepartment after update: {self.prod1.department}")
