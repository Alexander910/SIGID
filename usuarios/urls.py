from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('crear/', views.UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
]
