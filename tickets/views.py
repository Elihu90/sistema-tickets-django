from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
import datetime
from django.http import JsonResponse
from django.http import HttpResponse



from .forms import TicketForm, ActualizarEstadoForm
from .models import Ticket, TicketEstado, Herramienta, Notificacion

# ==============================================================================
# Vistas Principales (CRUD)
# ==============================================================================

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
def lista_tickets(request):
    """
    Muestra la lista de tickets con lógica de permisos.
    """
    if request.user.has_perm('tickets.view_ticket'):
        lista_de_tickets = Ticket.objects.all().order_by('-fecha_creacion')
        if request.user.has_perm('tickets.change_ticket'):
            for ticket in lista_de_tickets:
                ticket.form_estado = ActualizarEstadoForm(instance=ticket)
    else:
        lista_de_tickets = Ticket.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
    
    contexto = {'tickets': lista_de_tickets}
    return render(request, 'tickets/lista_tickets.html', contexto)


@login_required
def detalles_ticket(request, pk):
    """
    Muestra los detalles de un ticket con lógica de permisos.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.has_perm('tickets.view_ticket') and ticket.creado_por != request.user:
        messages.error(request, "No tienes permiso para ver este ticket.")
        return redirect('lista_tickets')
    
    contexto = {'ticket': ticket}
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


# ==============================================================================
# Vistas de Soporte (HTMX, Formularios pequeños, etc.)
# ==============================================================================

@login_required
def actualizar_estado_ticket(request, pk):
    if not request.user.has_perm('tickets.change_ticket'):
        # Devolvemos un error que también puede ser manejado por el frontend
        return HttpResponse(status=403) # 403 Forbidden

    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == 'POST':
        form = ActualizarEstadoForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            mensaje = f"Ticket {ticket.folio} actualizado a '{ticket.estado.nombre}'."

            # Creamos una respuesta vacía con una cabecera HX-Trigger
            response = HttpResponse(status=204) # 204 = Éxito, Sin Contenido
            response.headers['HX-Trigger'] = f'{{"showToast": {{"text": "{mensaje}", "type": "success"}}}}'
            return response
        else:
            # Si hay errores en el formulario
            mensaje = "Error al actualizar el ticket."
            response = HttpResponse(status=400) # 400 = Petición Inválida
            response.headers['HX-Trigger'] = f'{{"showToast": {{"text": "{mensaje}", "type": "error"}}}}'
            return response

    return HttpResponse(status=405) # 405 = Método no permitido si no es POST


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
    CORREGIDO: Esta vista ahora SOLO muestra las notificaciones, NO las marca como leídas.
    """
    notificaciones = Notificacion.objects.filter(usuario_destino=request.user, leido=False)
    return render(request, 'partials/lista_notificaciones.html', {'notificaciones': notificaciones})


# tickets/views.py

@login_required
def contar_notificaciones_sin_leer(request):
    print("--- Depurando la vista del contador de notificaciones ---")

    # 1. Verificamos quién es el usuario que está pidiendo la información
    print(f"Usuario de la petición: {request.user.username} (ID: {request.user.id})")

    # 2. Hacemos la consulta a la base de datos
    cantidad = Notificacion.objects.filter(usuario_destino=request.user, leido=False).count()

    # 3. Vemos qué resultado nos dio la consulta
    print(f"Notificaciones sin leer encontradas para este usuario: {cantidad}")
    print("-----------------------------------------------------")

    return render(request, 'partials/contador_notificaciones.html', {'cantidad_notificaciones': cantidad})

@login_required
def marcar_leida_y_redirigir(request, notificacion_pk):
    """
    Marca una notificación como leída y redirige al ticket asociado.
    """
    notificacion = get_object_or_404(Notificacion, pk=notificacion_pk, usuario_destino=request.user)
    notificacion.leido = True
    notificacion.save()
    return redirect('detalles_ticket', pk=notificacion.ticket.pk)


@login_required
def dashboard_service_line(request):
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # --- 1. Recopilar y aplicar todos los filtros ---
    end_date_str = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
    start_date_str = request.GET.get('start_date', (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
    estado_filtro = request.GET.get('estado')
    turno_filtro = request.GET.get('turno')
    fabricante_filtro = request.GET.get('fabricante')

    start_date = timezone.make_aware(datetime.datetime.strptime(start_date_str, '%Y-%m-%d'))
    end_date = timezone.make_aware(datetime.datetime.strptime(end_date_str, '%Y-%m-%d')) + datetime.timedelta(days=1)
    
    tickets_query = Ticket.objects.filter(fecha_creacion__range=(start_date, end_date))
    if estado_filtro: tickets_query = tickets_query.filter(estado__id=estado_filtro)
    if turno_filtro: tickets_query = tickets_query.filter(turno=turno_filtro)
    if fabricante_filtro: tickets_query = tickets_query.filter(herramienta__fabricante=fabricante_filtro)

    # --- 2. Calcular todas las estadísticas y KPIs ---
    
    # Gráfica de Estados
    conteo_por_estado = tickets_query.values('estado__nombre').annotate(total=Count('id')).order_by()
    color_map = {'Abierto': '#FF6384', 'En Reparacion': '#FFCE56', 'Cerrado': '#4BC0C0'}
    
    # Gráfica de Turnos
    conteo_por_turno = tickets_query.values('turno').annotate(total=Count('id')).order_by()
    
    # KPI de Eficiencia Ponderada
    total_tickets = tickets_query.count()
    tickets_cerrados_count = tickets_query.filter(estado__nombre='Cerrado').count()
    tickets_reparacion_count = tickets_query.filter(estado__nombre='En Reparacion').count()
    puntaje = (tickets_cerrados_count * 1) + (tickets_reparacion_count * 0.5)
    eficiencia_ponderada = round((puntaje / total_tickets) * 100, 1) if total_tickets > 0 else 0
    
    # Listas "Top 5"
    top_herramientas_fallas = tickets_query.values('herramienta__modelo').annotate(total=Count('id')).order_by('-total')[:5]
    top_tickets_antiguos = Ticket.objects.exclude(estado__nombre='Cerrado').order_by('fecha_creacion')[:5]

    # --- 3. Preparar el contexto completo para la plantilla ---
    contexto_completo = {
        'tickets': tickets_query.order_by('-fecha_creacion'),
        'start_date_value': start_date_str, 'end_date_value': end_date_str,
        'eficiencia_ponderada': eficiencia_ponderada,
        'top_tickets_antiguos': top_tickets_antiguos,
        'top_herramientas_fallas': top_herramientas_fallas,
        'opciones_estado': TicketEstado.objects.all(),
        'opciones_turno': Ticket.objects.filter(turno__isnull=False).values_list('turno', flat=True).distinct(),
        'opciones_fabricante': Herramienta.objects.values_list('fabricante', flat=True).distinct(),
        'contexto_graficas': {
            'estado_labels': [item['estado__nombre'] for item in conteo_por_estado],
            'estado_data': [item['total'] for item in conteo_por_estado],
            'estado_colors': [color_map.get(item['estado__nombre'], '#CCCCCC') for item in conteo_por_estado],
            'turno_labels': [item['turno'] or 'No asignado' for item in conteo_por_turno],
            'turno_data': [item['total'] for item in conteo_por_turno],
        }
    }

    for ticket in contexto_completo['tickets']:
        ticket.form_estado = ActualizarEstadoForm(instance=ticket)
    
    return render(request, 'tickets/dashboard.html', contexto_completo)




def verificar_ticket_duplicado(request, herramienta_pk):
    """
    Vista para HTMX: Busca tickets abiertos o en reparación para una herramienta específica.
    """
    # Buscamos tickets para esa herramienta cuyo estado NO sea 'Cerrado'
    tickets_abiertos = Ticket.objects.filter(
        herramienta_id=herramienta_pk
    ).exclude(
        estado__nombre='Cerrado'
    )

    contexto = {
        'tickets_duplicados': tickets_abiertos
    }
    # Renderiza la plantilla parcial que mostrará la advertencia
    return render(request, 'partials/advertencia_duplicado.html', contexto)



@login_required
def ticket_estado_data(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    conteo = Ticket.objects.values('estado__nombre').annotate(total=Count('id'))
    
    # --- LÓGICA DE COLORES AÑADIDA ---
    color_map = {
        'Abierto': 'rgba(255, 99, 132, 0.7)',   # Rojo
        'En Reparacion': 'rgba(255, 206, 86, 0.7)', # Amarillo
        'Cerrado': 'rgba(75, 192, 192, 0.7)',    # Verde
    }
    
    labels = [item['estado__nombre'] for item in conteo]
    data = [item['total'] for item in conteo]
    # Creamos una lista de colores en el mismo orden que las etiquetas
    background_colors = [color_map.get(label, '#CCCCCC') for label in labels] # Gris por defecto

    return JsonResponse({
        'labels': labels,
        'data': data,
        'colors': background_colors, # Enviamos los colores al frontend
    })
    
    
    
@login_required
def detalles_modelo_modal(request):
    # Solo para staff
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # Obtenemos el nombre del modelo desde los parámetros de la URL
    modelo_nombre = request.GET.get('modelo', None)
    tickets_del_modelo = []
    if modelo_nombre:
        tickets_del_modelo = Ticket.objects.filter(herramienta__modelo=modelo_nombre).order_by('-fecha_creacion')

    contexto = {
        'tickets': tickets_del_modelo,
        'modelo_nombre': modelo_nombre
    }
    return render(request, 'partials/modal_detalles_modelo.html', contexto)
