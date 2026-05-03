from django.urls import path
from . import views

app_name = 'alertas'

urlpatterns = [
    path('', views.AlertListView.as_view(), name='alert_list'),
    path('<int:pk>/leida/', views.AlertMarkReadView.as_view(), name='alert_mark_read'),
    path('marcar-todas/', views.AlertMarkAllReadView.as_view(), name='alert_mark_all_read'),
]
