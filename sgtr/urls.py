"""
URL configuration for sgtr project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Ruta principal
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('admin/', admin.site.urls),
    path('tickets/', include('tickets.urls')),
    path('inventario/', include('inventario.urls')),

    # Añade las URLs de login, logout, cambio de contraseña, etc.
    path('cuentas/', include('django.contrib.auth.urls')),
]