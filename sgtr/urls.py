"""
URL configuration for sgtr project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Ruta principal (Landing o Dashboard según estado)
    path('', views.index, name='home'),
    
    # Ruta específica para landing page (usada en logout)
    path('landing/', views.landing, name='landing'),

    path('admin/', admin.site.urls),
    path('tickets/', include('tickets.urls')),
    path('inventario/', include('inventario.urls')),

    # Añade las URLs de login, logout, cambio de contraseña, etc.
    path('cuentas/', include('django.contrib.auth.urls')),
]

# Servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
