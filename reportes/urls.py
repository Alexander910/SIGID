from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReportView.as_view(), name='report'),
    path('exportar/productos/', views.ExportProductsCSVView.as_view(), name='export_products'),
    path('exportar/movimientos/', views.ExportMovementsCSVView.as_view(), name='export_movements'),
]
