# tickets/views/crud.py

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.http import HttpRequest, HttpResponse

from tickets.forms import TicketForm, ActualizarEstadoForm, ComentarioForm
from tickets.models import Ticket, TicketEstado
from tickets.constants import Turno, TicketStatus

@login_required
def crear_ticket(request):
    """
    Maneja la creación de un nuevo ticket.
    Calcula la fecha y el turno, y genera un folio autoincremental.
    """
    ahora = timezone.localtime(timezone.now())
    hora_actual = ahora.time()

    if hora_actual >= datetime.time(6, 0) and hora_actual < datetime.time(14, 0):
        turno = Turno.PRIMERO
    elif hora_actual >= datetime.time(14, 0) and hora_actual < datetime.time(21, 30):
        turno = Turno.SEGUNDO
    else:
        turno = Turno.TERCERO

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                estado_abierto = TicketEstado.objects.get(nombre=TicketStatus.ABIERTO)
                nuevo_ticket = form.save(commit=False)
                
                nuevo_ticket.estado = estado_abierto
                nuevo_ticket.creado_por = request.user
                nuevo_ticket.turno = turno
                
                nuevo_ticket.save() # Primer guardado para obtener un ID
                nuevo_ticket.folio = f"TK{str(nuevo_ticket.id).zfill(8)}"
                nuevo_ticket.save() # Segundo guardado con el folio

                messages.success(request, f"¡Ticket {nuevo_ticket.folio} creado exitosamente!")
                return redirect('crear_ticket')
            except TicketEstado.DoesNotExist:
                messages.error(request, f"Error crítico: El estado '{TicketStatus.ABIERTO}' no existe. Por favor, créalo en el panel de administración.")
    else:
        form = TicketForm(initial={
            'fecha_actual': ahora.strftime("%d/%m/%Y %H:%M:%S"),
            'turno_actual': turno,
        })
    
    form.helper.form_action = reverse('crear_ticket')
    contexto = {
        'form': form,
        'titulo': 'Generar Nuevo Ticket de Reparación'
    }
    return render(request, 'tickets/crear_ticket.html', contexto)


@login_required
def lista_tickets(request: HttpRequest) -> HttpResponse:
    """
    Muestra la lista de tickets y pasa las opciones de estado para el formulario.
    """
    # Obtenemos todos los tickets, como antes
    if request.user.has_perm('tickets.view_ticket'):
        lista_de_tickets = Ticket.objects.all().order_by('-fecha_creacion')
    else:
        lista_de_tickets = Ticket.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
    
    # Obtenemos la lista de todos los estados posibles
    opciones_estado = TicketEstado.objects.all()
    
    contexto = {
        'tickets': lista_de_tickets,
        'opciones_estado': opciones_estado
    }
    return render(request, 'tickets/lista_tickets.html', contexto)

@login_required
def detalles_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Verificamos permisos de visualización
    if not request.user.has_perm('tickets.view_ticket') and ticket.creado_por != request.user:
        messages.error(request, "No tienes permiso para ver este ticket.")
        return redirect('lista_tickets')

    # Lógica para el historial de comentarios
    historial_comentarios = ticket.historial_comentarios.all()
    form_comentario = ComentarioForm()

    if request.method == 'POST' and 'guardar_comentario' in request.POST:
        form_comentario = ComentarioForm(request.POST)
        if form_comentario.is_valid():
            nuevo_comentario = form_comentario.save(commit=False)
            nuevo_comentario.ticket = ticket
            nuevo_comentario.autor = request.user
            nuevo_comentario.save()
            messages.success(request, "Comentario añadido exitosamente.")
            return redirect('detalles_ticket', pk=ticket.pk)

    # Lógica para el formulario de cambio de estado
    form_estado = ActualizarEstadoForm(instance=ticket)

    contexto = {
        'ticket': ticket,
        'form_estado': form_estado,
        'historial': historial_comentarios,
        'form_comentario': form_comentario,
    }
    return render(request, 'tickets/detalles_ticket.html', contexto)


@login_required
def editar_ticket(request, pk):
    """
    Maneja la edición de un ticket con lógica de permisos.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.has_perm('tickets.change_ticket') and ticket.creado_por != request.user:
        messages.error(request, "No tienes permiso para editar este ticket.")
        return redirect('lista_tickets')
    
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ticket {ticket.folio} actualizado exitosamente.")
            return redirect('detalles_ticket', pk=ticket.pk)
    else:
        form = TicketForm(instance=ticket)

    form.helper.form_action = reverse('editar_ticket', kwargs={'pk': ticket.pk})
    contexto = {'form': form, 'titulo': f'Editando Ticket: {ticket.folio}'}
    return render(request, 'tickets/crear_ticket.html', contexto)


@login_required
def eliminar_ticket(request, pk):
    """
    Maneja la eliminación de un ticket con lógica de permisos.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.has_perm('tickets.delete_ticket') and ticket.creado_por != request.user:
        messages.error(request, "No tienes permiso para eliminar este ticket.")
        return redirect('lista_tickets')
    
    if request.method == 'POST':
        folio_eliminado = ticket.folio
        ticket.delete()
        messages.success(request, f"El ticket {folio_eliminado} ha sido eliminado.")
        return redirect('lista_tickets')
        
    contexto = {'ticket': ticket}
    return render(request, 'tickets/eliminar_ticket.html', contexto)
