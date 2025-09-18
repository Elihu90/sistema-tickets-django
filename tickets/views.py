# tickets/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import TicketForm
from .models import Ticket, TicketEstado, Herramienta
import datetime
from django.utils import timezone

@login_required
def crear_ticket(request):
    ahora = timezone.localtime(timezone.now())
    hora_actual = ahora.time()

    # Lógica para determinar el turno
    if hora_actual >= datetime.time(6, 0) and hora_actual < datetime.time(14, 0):
        turno = "1er Turno"
    elif hora_actual >= datetime.time(14, 0) and hora_actual < datetime.time(21, 30):
        turno = "2do Turno"
    else:
        turno = "3er Turno"

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                estado_abierto = TicketEstado.objects.get(nombre='Abierto')
                nuevo_ticket = form.save(commit=False)

                # Asignamos los datos automáticos
                nuevo_ticket.estado = estado_abierto
                nuevo_ticket.creado_por = request.user
                nuevo_ticket.turno = turno # Guardamos el turno

                # --- NUEVA LÓGICA PARA EL FOLIO ---
                # 1. Guardamos una primera vez para obtener un ID
                nuevo_ticket.save() 

                # 2. Generamos el folio usando el ID
                nuevo_ticket.folio = f"TK{str(nuevo_ticket.id).zfill(8)}"

                # 3. Guardamos de nuevo ya con el folio
                nuevo_ticket.save()

                messages.success(request, f"¡Ticket {nuevo_ticket.folio} creado exitosamente!")
                return redirect('crear_ticket')
            except TicketEstado.DoesNotExist:
                messages.error(request, "Error crítico: El estado 'Abierto' no existe...")
    else:
        # Pre-poblamos el formulario con los datos automáticos
        form = TicketForm(initial={
            'fecha_actual': ahora.strftime("%d/%m/%Y %H:%M:%S"),
            'turno_actual': turno,
        })

    # ... (el resto de la vista se queda igual)
    form.helper.form_action = reverse('crear_ticket')
    contexto = {
        'form': form,
        'titulo': 'Generar Nuevo Ticket de Reparación'
    }
    return render(request, 'tickets/crear_ticket.html', contexto)

@login_required
def lista_tickets(request):
    # Esta era la función que faltaba en el código anterior
    tickets_del_usuario = Ticket.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
    contexto = {
        'tickets': tickets_del_usuario
    }
    return render(request, 'tickets/lista_tickets.html', contexto)

@login_required
def detalles_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, creado_por=request.user)
    contexto = {
        'ticket': ticket
    }
    return render(request, 'tickets/detalles_ticket.html', contexto)

@login_required
def editar_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, creado_por=request.user)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ticket {ticket.folio} actualizado exitosamente.")
            return redirect('detalles_ticket', pk=ticket.pk)
    else:
        form = TicketForm(instance=ticket)
    
    form.helper.form_action = reverse('editar_ticket', kwargs={'pk': ticket.pk})
    contexto = {
        'form': form,
        'titulo': f'Editando Ticket: {ticket.folio}'
    }
    return render(request, 'tickets/crear_ticket.html', contexto)

# --- Vistas para HTMX (Búsqueda dinámica) ---
def buscar_herramientas(request):
    query = request.POST.get('text_search', '')
    if query:
        herramientas = Herramienta.objects.filter(numero_serie__icontains=query) | Herramienta.objects.filter(modelo__icontains=query)
    else:
        herramientas = []
    return render(request, 'tickets/partials/search_results.html', {'herramientas': herramientas})

def detalles_herramienta(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    return render(request, 'tickets/partials/herramienta_details.html', {'herramienta': herramienta})