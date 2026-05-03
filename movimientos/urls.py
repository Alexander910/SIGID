from django.urls import path
from . import views

app_name = 'movimientos'

urlpatterns = [
    path('', views.MovementListView.as_view(), name='movement_list'),
    path('crear/', views.MovementCreateView.as_view(), name='movement_create'),
]
