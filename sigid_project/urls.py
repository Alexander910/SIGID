"""
URL Configuration for SIGID.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Autenticación ──
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ── Apps ──
    path('', include('inventario.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('movimientos/', include('movimientos.urls')),
    path('alertas/', include('alertas.urls')),
    path('reportes/', include('reportes.urls')),
]
