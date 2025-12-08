from django.urls import path
from . import views

urlpatterns = [
    # Herramienta CRUD
    path('herramientas/', views.HerramientaListView.as_view(), name='herramienta_list'),
    path('herramientas/add/', views.HerramientaCreateView.as_view(), name='herramienta_add'),
    path('herramientas/<int:pk>/edit/', views.HerramientaUpdateView.as_view(), name='herramienta_edit'),
    path('herramientas/<int:pk>/delete/', views.HerramientaDeleteView.as_view(), name='herramienta_delete'),
    # Colaborador CRUD
    path('colaboradores/', views.ColaboradorListView.as_view(), name='colaborador_list'),
    path('colaboradores/add/', views.ColaboradorCreateView.as_view(), name='colaborador_add'),
    path('colaboradores/<int:pk>/edit/', views.ColaboradorUpdateView.as_view(), name='colaborador_edit'),
    path('colaboradores/<int:pk>/delete/', views.ColaboradorDeleteView.as_view(), name='colaborador_delete'),
    # Refaccion CRUD
    path('refacciones/', views.RefaccionListView.as_view(), name='refaccion_list'),
    path('refacciones/add/', views.RefaccionCreateView.as_view(), name='refaccion_add'),
    path('refacciones/<int:pk>/edit/', views.RefaccionUpdateView.as_view(), name='refaccion_edit'),
    path('refacciones/<int:pk>/delete/', views.RefaccionDeleteView.as_view(), name='refaccion_delete'),
]
