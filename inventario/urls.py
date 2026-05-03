from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('inventario/', views.ProductListView.as_view(), name='product_list'),
    path('inventario/crear/', views.ProductCreateView.as_view(), name='product_create'),
    path('inventario/<int:pk>/editar/', views.ProductUpdateView.as_view(), name='product_update'),
    path('inventario/<int:pk>/eliminar/', views.ProductDeleteView.as_view(), name='product_delete'),
]
