from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Herramienta, Refaccion
from usuarios.models import Colaborador
from .forms import ColaboradorForm

# Herramienta CRUD views
class HerramientaListView(ListView):
    model = Herramienta
    template_name = 'inventario/herramienta_list.html'
    context_object_name = 'herramientas'

    def get_queryset(self):
        return Herramienta.objects.filter(activo=True)

class HerramientaCreateView(CreateView):
    model = Herramienta
    fields = ['numero_serie', 'numero_reparacion', 'tipo', 'fabricante', 'modelo', 'estado', 'ejecucion', 'ubicacion', 'activo']
    template_name = 'inventario/herramienta_form.html'
    success_url = reverse_lazy('herramienta_list')

class HerramientaUpdateView(UpdateView):
    model = Herramienta
    fields = ['numero_serie', 'numero_reparacion', 'tipo', 'fabricante', 'modelo', 'estado', 'ejecucion', 'ubicacion', 'activo']
    template_name = 'inventario/herramienta_form.html'
    success_url = reverse_lazy('herramienta_list')

from django.db.models import ProtectedError
from django.contrib import messages
from django.shortcuts import redirect

class HerramientaDeleteView(DeleteView):
    model = Herramienta
    template_name = 'inventario/herramienta_confirm_delete.html'
    success_url = reverse_lazy('herramienta_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')

        if action == 'soft':
            self.object.activo = False
            self.object.save()
            messages.success(request, f"La herramienta '{self.object}' ha sido dada de baja (Soft Delete).")
            return redirect(self.success_url)
        
        elif action == 'hard':
            try:
                # Eliminación en cascada manual para tickets protegidos
                tickets_asociados = self.object.ticket_set.all()
                count = tickets_asociados.count()
                tickets_asociados.delete() # Borra los tickets primero
                self.object.delete() # Luego la herramienta
                messages.warning(request, f"Se eliminó la herramienta '{self.object}' y sus {count} tickets asociados permanentemente.")
                return redirect(self.success_url)
            except ProtectedError:
                messages.error(request, "No se pudo eliminar la herramienta debido a otras dependencias protegidas.")
                return redirect('herramienta_list')
        
        # Default behavior (shouldn't happen with correct template)
        return redirect('herramienta_list')

# Colaborador CRUD views
class ColaboradorListView(ListView):
    model = Colaborador
    template_name = 'inventario/colaborador_list.html'
    context_object_name = 'colaboradores'

    def get_queryset(self):
        return Colaborador.objects.filter(activo=True)

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')

        if action == 'soft':
            self.object.activo = False
            self.object.save()
            # Opcional: Desactivar también el usuario de Django para impedir login
            self.object.usuario.is_active = False
            self.object.usuario.save()
            messages.success(request, f"El colaborador '{self.object}' ha sido dado de baja (Soft Delete).")
            return redirect(self.success_url)
        
        elif action == 'hard':
            try:
                user = self.object.usuario
                user.delete() # Esto borrará el Colaborador en cascada
                messages.warning(request, f"Se eliminó permanentemente al colaborador '{self.object}' y su usuario asociado.")
                return redirect(self.success_url)
            except ProtectedError:
                messages.error(request, "No se puede eliminar el colaborador porque tiene registros asociados (Tickets, etc.). Intenta darlo de baja.")
                return redirect('colaborador_list')
        
        return redirect('colaborador_list')


# Refaccion CRUD views
class RefaccionListView(ListView):
    model = Refaccion
    template_name = 'inventario/refaccion_list.html'
    context_object_name = 'refacciones'

    def get_queryset(self):
        return Refaccion.objects.filter(activo=True)

class RefaccionCreateView(CreateView):
    model = Refaccion
    fields = ['numero_sap', 'descripcion', 'cantidad', 'ubicacion_almacen', 'precio_unitario', 'proveedor', 'notas', 'imagen', 'activo']
    template_name = 'inventario/refaccion_form.html'
    success_url = reverse_lazy('refaccion_list')

class RefaccionUpdateView(UpdateView):
    model = Refaccion
    fields = ['numero_sap', 'descripcion', 'cantidad', 'ubicacion_almacen', 'precio_unitario', 'proveedor', 'notas', 'imagen', 'activo']
    template_name = 'inventario/refaccion_form.html'
    success_url = reverse_lazy('refaccion_list')

class RefaccionDeleteView(DeleteView):
    model = Refaccion
    template_name = 'inventario/refaccion_confirm_delete.html'
    success_url = reverse_lazy('refaccion_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')

        if action == 'soft':
            self.object.activo = False
            self.object.save()
            messages.success(request, f"La refacción '{self.object}' ha sido dada de baja (Soft Delete).")
            return redirect(self.success_url)
        
        elif action == 'hard':
            try:
                self.object.delete()
                messages.warning(request, f"Se eliminó permanentemente la refacción '{self.object}'.")
                return redirect(self.success_url)
            except ProtectedError:
                messages.error(request, "No se pudo eliminar la refacción debido a dependencias protegidas.")
                return redirect('refaccion_list')
        
        return redirect('refaccion_list')

