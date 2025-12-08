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
                # Redirigir con el ID del ticket para activar el modal de impresión
                return redirect(reverse('crear_ticket') + f'?ticket_creado={nuevo_ticket.id}')
            except TicketEstado.DoesNotExist:
                messages.error(request, f"Error crítico: El estado '{TicketStatus.ABIERTO}' no existe. Por favor, créalo en el panel de administración.")
    else:
        form = TicketForm(initial={
            'fecha_actual': ahora.strftime("%d/%m/%Y %H:%M:%S"),
            'turno_actual': turno,
        })
    
    # Verificar si venimos de crear un ticket para mostrar el modal
    ticket_creado_id = request.GET.get('ticket_creado')
    ticket_creado = None
    if ticket_creado_id:
        try:
            ticket_creado = Ticket.objects.get(id=ticket_creado_id)
        except Ticket.DoesNotExist:
            pass

    form.helper.form_action = reverse('crear_ticket')
    contexto = {
        'form': form,
        'titulo': 'Generar Nuevo Ticket de Reparación',
        'ticket_creado': ticket_creado  # Pasamos el objeto al template
    }
    return render(request, 'tickets/crear_ticket.html', contexto)


from django.db.models import Q

@login_required
def lista_tickets(request: HttpRequest) -> HttpResponse:
    """
    Muestra la lista de tickets con opciones de búsqueda y filtrado.
    """
    # 1. Base QuerySet con optimización
    queryset = Ticket.objects.select_related(
        'estado', 'herramienta', 'ubicacion', 'creado_por', 'falla'
    ).order_by('-fecha_creacion')

    # 2. Filtrar por permisos (Usuario normal solo ve sus tickets)
    if not request.user.has_perm('tickets.view_ticket'):
        queryset = queryset.filter(creado_por=request.user)

    # 3. Obtener parámetros de búsqueda del GET
    busqueda = request.GET.get('q', '')
    estado_id = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # 4. Aplicar Filtros
    
    # Búsqueda general (Folio, Herramienta, Falla)
    if busqueda:
        queryset = queryset.filter(
            Q(folio__icontains=busqueda) |
            Q(herramienta__numero_serie__icontains=busqueda) |
            Q(herramienta__modelo__icontains=busqueda) |
            Q(falla__descripcion__icontains=busqueda) |
            Q(comentarios__icontains=busqueda)
        )

    # Filtro por Estado
    if estado_id:
        queryset = queryset.filter(estado_id=estado_id)

    # Filtro por Rango de Fechas
    if fecha_inicio:
        try:
            # Convertir string a fecha consciente de zona horaria si es necesario
            # Asumimos formato YYYY-MM-DD que envía el input type="date"
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_inicio)
        except ValueError:
            pass # Ignorar formato inválido

    if fecha_fin:
        try:
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_fin)
        except ValueError:
            pass

    # 5. Obtener opciones para los selects
    opciones_estado = TicketEstado.objects.all()
    
    contexto = {
        'tickets': queryset,
        'opciones_estado': opciones_estado,
        # Mantener los valores en el formulario después de buscar
        'busqueda_actual': busqueda,
        'estado_actual': int(estado_id) if estado_id.isdigit() else '',
        'fecha_inicio_actual': fecha_inicio,
        'fecha_fin_actual': fecha_fin,
    }
    return render(request, 'tickets/lista_tickets.html', contexto)

@login_required
def detalles_ticket(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'estado', 'herramienta', 'ubicacion', 'creado_por', 'falla'
        ).prefetch_related('historial_comentarios__autor'),
        pk=pk
    )
    
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


from django.db.models import Q

@login_required
def lista_tickets(request: HttpRequest) -> HttpResponse:
    """
    Muestra la lista de tickets con opciones de búsqueda y filtrado.
    """
    # 1. Base QuerySet con optimización
    queryset = Ticket.objects.select_related(
        'estado', 'herramienta', 'ubicacion', 'creado_por', 'falla'
    ).order_by('-fecha_creacion')

    # 2. Filtrar por permisos (Usuario normal solo ve sus tickets)
    if not request.user.has_perm('tickets.view_ticket'):
        queryset = queryset.filter(creado_por=request.user)

    # 3. Obtener parámetros de búsqueda del GET
    busqueda = request.GET.get('q', '')
    estado_id = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # 4. Aplicar Filtros
    
    # Búsqueda general (Folio, Herramienta, Falla)
    if busqueda:
        queryset = queryset.filter(
            Q(folio__icontains=busqueda) |
            Q(herramienta__numero_serie__icontains=busqueda) |
            Q(herramienta__modelo__icontains=busqueda) |
            Q(falla__descripcion__icontains=busqueda) |
            Q(comentarios__icontains=busqueda)
        )

    # Filtro por Estado
    if estado_id:
        queryset = queryset.filter(estado_id=estado_id)

    # Filtro por Rango de Fechas
    if fecha_inicio:
        try:
            # Convertir string a fecha consciente de zona horaria si es necesario
            # Asumimos formato YYYY-MM-DD que envía el input type="date"
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_inicio)
        except ValueError:
            pass # Ignorar formato inválido

    if fecha_fin:
        try:
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_fin)
        except ValueError:
            pass

    # 5. Obtener opciones para los selects
    opciones_estado = TicketEstado.objects.all()
    
    contexto = {
        'tickets': queryset,
        'opciones_estado': opciones_estado,
        # Mantener los valores en el formulario después de buscar
        'busqueda_actual': busqueda,
        'estado_actual': int(estado_id) if estado_id.isdigit() else '',
        'fecha_inicio_actual': fecha_inicio,
        'fecha_fin_actual': fecha_fin,
    }
    return render(request, 'tickets/lista_tickets.html', contexto)

@login_required
def detalles_ticket(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'estado', 'herramienta', 'ubicacion', 'creado_por', 'falla'
        ).prefetch_related('historial_comentarios__autor'),
        pk=pk
    )
    
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
    Elimina un ticket si el usuario tiene permiso.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.has_perm('tickets.delete_ticket'):
         messages.error(request, "No tienes permiso para eliminar tickets.")
         return redirect('lista_tickets')
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, "Ticket eliminado correctamente.")
        return redirect('lista_tickets')
        
    return render(request, 'tickets/confirmar_eliminar.html', {'ticket': ticket})

@login_required
def imprimir_etiqueta(request, pk):
    """
    Genera una página HTML optimizada para impresión de etiquetas (75mm x 24mm).
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    # Permisos? Todos los que pueden ver deberían poder imprimir.
    # Usamos la misma lógica básica de permisos que detalles_ticket
    if not request.user.has_perm('tickets.view_ticket') and ticket.creado_por != request.user:
        messages.error(request, "No tienes permiso para imprimir este ticket.")
        return redirect('lista_tickets')
        
    return render(request, 'tickets/etiqueta.html', {'ticket': ticket})
