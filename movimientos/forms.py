from django import forms
from inventario.models import Product
from .models import Movement


class MovementForm(forms.ModelForm):
    """Formulario para registrar movimientos de inventario."""

    class Meta:
        model = Movement
        fields = ['product', 'type', 'quantity', 'observation']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
            }),
            'observation': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Filtrar productos por departamento
        if user and user.role != 'admin':
            self.fields['product'].queryset = Product.objects.filter(
                department=user.department
            )
