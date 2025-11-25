from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Herramienta
from usuarios.models import Colaborador
from .forms import ColaboradorForm

# Herramienta CRUD views
class HerramientaListView(ListView):
    model = Herramienta
    template_name = 'inventario/herramienta_list.html'
    context_object_name = 'herramientas'

class HerramientaCreateView(CreateView):
    model = Herramienta
    fields = ['numero_serie', 'numero_reparacion', 'tipo', 'fabricante', 'modelo', 'estado', 'ejecucion', 'ubicacion']
    template_name = 'inventario/herramienta_form.html'
    success_url = reverse_lazy('herramienta_list')

class HerramientaUpdateView(UpdateView):
    model = Herramienta
    fields = ['numero_serie', 'numero_reparacion', 'tipo', 'fabricante', 'modelo', 'estado', 'ejecucion', 'ubicacion']
    template_name = 'inventario/herramienta_form.html'
    success_url = reverse_lazy('herramienta_list')

class HerramientaDeleteView(DeleteView):
    model = Herramienta
    template_name = 'inventario/herramienta_confirm_delete.html'
    success_url = reverse_lazy('herramienta_list')

# Colaborador CRUD views
class ColaboradorListView(ListView):
    model = Colaborador
    template_name = 'inventario/colaborador_list.html'
    context_object_name = 'colaboradores'

class ColaboradorCreateView(CreateView):
    model = Colaborador
    form_class = ColaboradorForm
    template_name = 'inventario/colaborador_form.html'
    success_url = reverse_lazy('colaborador_list')

class ColaboradorUpdateView(UpdateView):
    model = Colaborador
    form_class = ColaboradorForm
    template_name = 'inventario/colaborador_form.html'
    success_url = reverse_lazy('colaborador_list')

class ColaboradorDeleteView(DeleteView):
    model = Colaborador
    template_name = 'inventario/colaborador_confirm_delete.html'
    success_url = reverse_lazy('colaborador_list')
