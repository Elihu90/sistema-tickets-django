# tickets/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Esta URL corresponderá a la vista para crear tickets
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('lista/', views.lista_tickets, name='lista_tickets'),
    path('buscar-herramientas/', views.buscar_herramientas, name='buscar_herramientas'),
    path('detalles-herramienta/<int:pk>/', views.detalles_herramienta, name='detalles_herramienta'),
]