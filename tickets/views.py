from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
import datetime

from .forms import TicketForm, ActualizarEstadoForm
from .models import Ticket, TicketEstado, Herramienta, Notificacion

# ==============================================================================
# Vistas Principales (CRUD)
# ==============================================================================

@login_required
def lista_tickets(request):
    """
    Muestra la lista de tickets.
    - Si el usuario es admin/staff, muestra TODOS los tickets.
    - Si es un usuario normal, muestra solo los suyos.
    Para los admins, adjunta un formulario para cambiar el estado de cada ticket.
    """
    if request.user.is_staff:
        lista_de_tickets = Ticket.objects.all().order_by('-fecha_creacion')
        # Adjuntamos una instancia del formulario a cada ticket para los admins
        for ticket in lista_de_tickets:
            ticket.form_estado = ActualizarEstadoForm(instance=ticket)
    else:
        lista_de_tickets = Ticket.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
    
    contexto = {
        'tickets': lista_de_tickets
    }
    return render(request, 'tickets/lista_tickets.html', contexto)


@login_required
def detalles_ticket(request, pk):
    """
    Muestra los detalles completos de un ticket específico.
    Los admins pueden ver cualquier ticket, los usuarios solo los suyos.
    """
    if request.user.is_staff:
        ticket = get_object_or_404(Ticket, pk=pk)
    else:
        ticket = get_object_or_404(Ticket, pk=pk, creado_por=request.user)
    
    contexto = {
        'ticket': ticket
    }
    return render(request, 'tickets/detalles_ticket.html', contexto)


@login_required
def crear_ticket(request):
    """
    Maneja la creación de un nuevo ticket.
    Calcula la fecha y el turno, y genera un folio autoincremental.
    """
    ahora = timezone.localtime(timezone.now())
    hora_actual = ahora.time()

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
                
                nuevo_ticket.estado = estado_abierto
                nuevo_ticket.creado_por = request.user
                nuevo_ticket.turno = turno
                
                nuevo_ticket.save() # Primer guardado para obtener un ID
                nuevo_ticket.folio = f"TK{str(nuevo_ticket.id).zfill(8)}"
                nuevo_ticket.save() # Segundo guardado con el folio

                messages.success(request, f"¡Ticket {nuevo_ticket.folio} creado exitosamente!")
                return redirect('crear_ticket')
            except TicketEstado.DoesNotExist:
                messages.error(request, "Error crítico: El estado 'Abierto' no existe. Por favor, créalo en el panel de administración.")
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
def editar_ticket(request, pk):
    """
    Maneja la edición de un ticket existente.
    Los admins pueden editar cualquier ticket, los usuarios solo los suyos.
    """
    if request.user.is_staff:
        ticket = get_object_or_404(Ticket, pk=pk)
    else:
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


@login_required
def eliminar_ticket(request, pk):
    """
    Maneja la eliminación de un ticket, con una página de confirmación.
    Los admins pueden eliminar cualquier ticket, los usuarios solo los suyos.
    """
    if request.user.is_staff:
        ticket = get_object_or_404(Ticket, pk=pk)
    else:
        ticket = get_object_or_404(Ticket, pk=pk, creado_por=request.user)

    if request.method == 'POST':
        folio_eliminado = ticket.folio
        ticket.delete()
        messages.success(request, f"El ticket {folio_eliminado} ha sido eliminado.")
        return redirect('lista_tickets')
    
    contexto = {
        'ticket': ticket
    }
    return render(request, 'tickets/eliminar_ticket.html', contexto)


# ==============================================================================
# Vistas de Soporte y HTMX
# ==============================================================================

@login_required
def actualizar_estado_ticket(request, pk):
    """
    Procesa el cambio de estado desde el formulario en la lista de tickets.
    Solo accesible para personal de staff.
    """
    if not request.user.is_staff:
        return redirect('lista_tickets')

    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        form = ActualizarEstadoForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, f"El estado del ticket {ticket.folio} ha sido actualizado.")
    
    return redirect('lista_tickets')


def buscar_herramientas(request):
    """
    Vista para HTMX: Busca herramientas y devuelve una lista de resultados.
    """
    query = request.POST.get('text_search', '')
    if query:
        herramientas = Herramienta.objects.filter(numero_serie__icontains=query) | Herramienta.objects.filter(modelo__icontains=query)
    else:
        herramientas = []
    return render(request, 'tickets/partials/search_results.html', {'herramientas': herramientas})


@login_required
def ver_notificaciones(request):
    """
    Vista para HTMX: Muestra las notificaciones no leídas y las marca como leídas.
    """
    notificaciones = Notificacion.objects.filter(usuario_destino=request.user, leido=False)
    notificaciones.update(leido=True)
    return render(request, 'partials/lista_notificaciones.html', {'notificaciones': notificaciones})


@login_required
def contar_notificaciones_sin_leer(request):
    """
    Vista para HTMX: Devuelve la cantidad de notificaciones no leídas para el badge.
    """
    cantidad = Notificacion.objects.filter(usuario_destino=request.user, leido=False).count()
    return render(request, 'partials/contador_notificaciones.html', {'cantidad_notificaciones': cantidad})


# ==============================================================================
# Vistas para Notificaciones y HTMX
# ==============================================================================

@login_required
def ver_notificaciones(request):
    """
    Vista para HTMX: Muestra las notificaciones NO leídas.
    Esta versión corregida YA NO las marca como leídas, solo las muestra.
    """
    notificaciones = Notificacion.objects.filter(usuario_destino=request.user, leido=False)
    return render(request, 'partials/lista_notificaciones.html', {'notificaciones': notificaciones})


@login_required
def contar_notificaciones_sin_leer(request):
    """
    Vista para HTMX: Devuelve la cantidad de notificaciones no leídas para el badge.
    """
    cantidad = Notificacion.objects.filter(usuario_destino=request.user, leido=False).count()
    return render(request, 'partials/contador_notificaciones.html', {'cantidad_notificaciones': cantidad})


@login_required
def marcar_leida_y_redirigir(request, notificacion_pk):
    """
    NUEVA VISTA: Marca una notificación específica como leída y redirige al ticket asociado.
    """
    # Buscamos la notificación y nos aseguramos que pertenezca al usuario actual
    notificacion = get_object_or_404(Notificacion, pk=notificacion_pk, usuario_destino=request.user)
    
    # La marcamos como leída
    notificacion.leido = True
    notificacion.save()
    
    # Redirigimos al usuario a la página de detalles del ticket
    return redirect('detalles_ticket', pk=notificacion.ticket.pk)