from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy

from core.mixins import AdminRequiredMixin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserListView(AdminRequiredMixin, ListView):
    """Lista de usuarios (solo admin)."""
    model = User
    template_name = 'usuarios/user_list.html'
    context_object_name = 'users'
    paginate_by = 20


class UserCreateView(AdminRequiredMixin, CreateView):
    """Crear usuario (solo admin)."""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:user_list')


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Editar usuario (solo admin)."""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'usuarios/user_form.html'
    success_url = reverse_lazy('usuarios:user_list')
