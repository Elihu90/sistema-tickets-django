"""
URL configuration for sgtr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# sgtr/urls.py

# sgtr/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # <-- Importar RedirectView

urlpatterns = [
    # Ruta principal que redirige a la creación de tickets
    path('', RedirectView.as_view(url='/tickets/crear/', permanent=True)),

    path('admin/', admin.site.urls),
    path('tickets/', include('tickets.urls')),

    # Añade las URLs de login, logout, cambio de contraseña, etc.
    path('cuentas/', include('django.contrib.auth.urls')),
]