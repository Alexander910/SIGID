from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Formulario para crear/editar productos."""

    class Meta:
        model = Product
        fields = [
            'name', 'code', 'category', 'department',
            'description', 'quantity', 'min_stock',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
            }),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Encargados: solo su departamento
        if user and user.role != 'admin':
            self.fields['department'].initial = user.department
            self.fields['department'].widget = forms.HiddenInput()
