# tickets/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('lista/', views.lista_tickets, name='lista_tickets'),
    path('detalles/<int:pk>/', views.detalles_ticket, name='detalles_ticket'),
    path('editar/<int:pk>/', views.editar_ticket, name='editar_ticket'),
    path('eliminar/<int:pk>/', views.eliminar_ticket, name='eliminar_ticket'),
    
    # URL para actualizar estado
    path('actualizar-estado/<int:pk>/', views.actualizar_estado_ticket, name='actualizar_estado_ticket'),
    
    # URL para la búsqueda de HTMX
    path('buscar-herramientas/', views.buscar_herramientas, name='buscar_herramientas'),
    
    # URLs para Notificaciones
    path('notificaciones/', views.ver_notificaciones, name='ver_notificaciones'),
    path('notificaciones/contador/', views.contar_notificaciones_sin_leer, name='contar_notificaciones_sin_leer'),
    path('notificaciones/leer/<int:notificacion_pk>/', views.marcar_leida_y_redirigir, name='marcar_leida_y_redirigir'),

]