from django.shortcuts import render

# Create your views here.
"""
Vistas para la aplicación de tickets.
Maneja CRUD de tickets, dashboard, exportación y notificaciones.
"""

import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from .forms import ActualizarEstadoForm, ComentarioForm, TicketForm
from .models import (
    Comentario,
    Herramienta,
    Notificacion,
    Ticket,
    TicketEstado,
)


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

    # Determinar el turno según la hora
    if datetime.time(6, 0) <= hora_actual < datetime.time(14, 0):
        turno = "1er Turno"
    elif datetime.time(14, 0) <= hora_actual < datetime.time(21, 30):
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

                nuevo_ticket.save()  # Primer guardado para obtener un ID
                nuevo_ticket.folio = f"TK{str(nuevo_ticket.id).zfill(8)}"
                nuevo_ticket.save()  # Segundo guardado con el folio

                messages.success(
                    request,
                    f"¡Ticket {nuevo_ticket.folio} creado exitosamente!"
                )
                return redirect('crear_ticket')
            except TicketEstado.DoesNotExist:
                messages.error(
                    request,
                    "Error crítico: El estado 'Abierto' no existe. "
                    "Por favor, créalo en el panel de administración."
                )
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
    Muestra la lista de tickets y pasa las opciones de estado para el
    formulario.
    """
    # Obtenemos todos los tickets según permisos
    if request.user.has_perm('tickets.view_ticket'):
        lista_de_tickets = Ticket.objects.all().order_by('-fecha_creacion')
    else:
        lista_de_tickets = Ticket.objects.filter(
            creado_por=request.user
        ).order_by('-fecha_creacion')

    # Obtenemos la lista de todos los estados posibles
    opciones_estado = TicketEstado.objects.all()

    contexto = {
        'tickets': lista_de_tickets,
        'opciones_estado': opciones_estado
    }
    return render(request, 'tickets/lista_tickets.html', contexto)


@login_required
def detalles_ticket(request, pk):
    """
    Muestra los detalles de un ticket con historial de comentarios.
    Permite agregar comentarios.
    """
    ticket = get_object_or_404(Ticket, pk=pk)

    # Verificamos permisos de visualización
    puede_ver = (
        request.user.has_perm('tickets.view_ticket') or
        ticket.creado_por == request.user
    )
    if not puede_ver:
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
    puede_editar = (
        request.user.has_perm('tickets.change_ticket') or
        ticket.creado_por == request.user
    )
    if not puede_editar:
        messages.error(request, "No tienes permiso para editar este ticket.")
        return redirect('lista_tickets')

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Ticket {ticket.folio} actualizado exitosamente."
            )
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
    Maneja la eliminación de un ticket con lógica de permisos.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    puede_eliminar = (
        request.user.has_perm('tickets.delete_ticket') or
        ticket.creado_por == request.user
    )
    if not puede_eliminar:
        messages.error(request, "No tienes permiso para eliminar este ticket.")
        return redirect('lista_tickets')

    if request.method == 'POST':
        folio_eliminado = ticket.folio
        ticket.delete()
        messages.success(
            request,
            f"El ticket {folio_eliminado} ha sido eliminado."
        )
        return redirect('lista_tickets')

    contexto = {'ticket': ticket}
    return render(request, 'tickets/eliminar_ticket.html', contexto)


# ==============================================================================
# Vistas de Soporte (HTMX, Formularios pequeños, etc.)
# ==============================================================================

@login_required
def actualizar_estado_ticket(request, pk):
    """
    Actualiza el estado de un ticket vía HTMX.
    """
    if not request.user.has_perm('tickets.change_ticket'):
        return HttpResponse(status=403)  # 403 Forbidden

    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == 'POST':
        form = ActualizarEstadoForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            mensaje = (
                f"Ticket {ticket.folio} actualizado a "
                f"'{ticket.estado.nombre}'."
            )

            # Respuesta con cabecera HX-Trigger para toast
            response = HttpResponse(status=204)  # 204 = Éxito, Sin Contenido
            trigger_data = json.dumps({
                "showToast": {
                    "text": mensaje,
                    "type": "success"
                }
            })
            response.headers['HX-Trigger'] = trigger_data
            return response
        else:
            # Si hay errores en el formulario
            mensaje = "Error al actualizar el ticket."
            response = HttpResponse(status=400)  # 400 = Petición Inválida
            trigger_data = json.dumps({
                "showToast": {
                    "text": mensaje,
                    "type": "error"
                }
            })
            response.headers['HX-Trigger'] = trigger_data
            return response

    return HttpResponse(status=405)  # 405 = Método no permitido


def buscar_herramientas(request):
    """
    Vista para HTMX: Busca herramientas y devuelve una lista de resultados.
    """
    query = request.POST.get('text_search', '')
    if query:
        herramientas = (
            Herramienta.objects.filter(numero_serie__icontains=query) |
            Herramienta.objects.filter(modelo__icontains=query)
        )
    else:
        herramientas = []

    return render(
        request,
        'tickets/partials/search_results.html',
        {'herramientas': herramientas}
    )


@login_required
def ver_notificaciones(request):
    """
    Muestra las notificaciones sin leer del usuario.
    Esta vista NO marca las notificaciones como leídas.
    """
    notificaciones = Notificacion.objects.filter(
        usuario_destino=request.user,
        leido=False
    )
    return render(
        request,
        'partials/lista_notificaciones.html',
        {'notificaciones': notificaciones}
    )


@login_required
def contar_notificaciones_sin_leer(request):
    """
    Cuenta las notificaciones sin leer para el usuario actual.
    """
    print("--- Depurando la vista del contador de notificaciones ---")
    print(
        f"Usuario de la petición: {request.user.username} "
        f"(ID: {request.user.id})"
    )

    cantidad = Notificacion.objects.filter(
        usuario_destino=request.user,
        leido=False
    ).count()

    print(f"Notificaciones sin leer encontradas: {cantidad}")
    print("-----------------------------------------------------")

    return render(
        request,
        'partials/contador_notificaciones.html',
        {'cantidad_notificaciones': cantidad}
    )


@login_required
def marcar_leida_y_redirigir(request, notificacion_pk):
    """
    Marca una notificación como leída y redirige al ticket asociado.
    """
    notificacion = get_object_or_404(
        Notificacion,
        pk=notificacion_pk,
        usuario_destino=request.user
    )
    notificacion.leido = True
    notificacion.save()
    return redirect('detalles_ticket', pk=notificacion.ticket.pk)


@login_required
def verificar_ticket_duplicado(request, herramienta_pk):
    """
    Vista para HTMX: Busca tickets abiertos o en reparación para una
    herramienta específica.
    """
    tickets_abiertos = Ticket.objects.filter(
        herramienta_id=herramienta_pk
    ).exclude(
        estado__nombre='Cerrado'
    )

    contexto = {'tickets_duplicados': tickets_abiertos}
    return render(request, 'partials/advertencia_duplicado.html', contexto)


@login_required
def ticket_estado_data(request):
    """
    API endpoint que devuelve datos JSON sobre el conteo de tickets por estado.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    conteo = Ticket.objects.values('estado__nombre').annotate(total=Count('id'))

    color_map = {
        'Abierto': 'rgba(255, 99, 132, 0.7)',  # Rojo
        'En Reparacion': 'rgba(255, 206, 86, 0.7)',  # Amarillo
        'Cerrado': 'rgba(75, 192, 192, 0.7)',  # Verde
    }

    labels = [item['estado__nombre'] for item in conteo]
    data = [item['total'] for item in conteo]
    background_colors = [
        color_map.get(label, '#CCCCCC') for label in labels
    ]

    return JsonResponse({
        'labels': labels,
        'data': data,
        'colors': background_colors,
    })


# ==============================================================================
# Dashboard y Reportes
# ==============================================================================

@login_required
def dashboard_service_line(request):
    """
    Dashboard principal con estadísticas, gráficas y filtros.
    """
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # --- 1. Recopilar y aplicar filtros ---
    end_date_str = request.GET.get(
        'end_date',
        timezone.now().strftime('%Y-%m-%d')
    )
    start_date_str = request.GET.get(
        'start_date',
        (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    )

    estado_filtro_str = request.GET.get('estado')
    turno_filtro = request.GET.get('turno')
    fabricante_filtro = request.GET.get('fabricante')

    start_date = timezone.make_aware(
        datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    )
    end_date = timezone.make_aware(
        datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    ) + datetime.timedelta(days=1)

    # Consulta base para KPI
    base_query = Ticket.objects.filter(
        fecha_creacion__range=(start_date, end_date)
    )

    # Consulta filtrada para gráficas y tablas
    tickets_query = base_query

    if estado_filtro_str and estado_filtro_str.isdigit():
        tickets_query = tickets_query.filter(estado__id=int(estado_filtro_str))

    if turno_filtro:
        tickets_query = tickets_query.filter(turno=turno_filtro)

    if fabricante_filtro:
        tickets_query = tickets_query.filter(
            herramienta__fabricante=fabricante_filtro
        )

    # --- 2. Calcular estadísticas ---
    color_map = {
        'Abierto': '#FF6384',
        'En Reparación': '#FFCE56',
        'Cerrado': '#4BC0C0'
    }

    # KPI de eficiencia (calculado sobre base_query sin filtro de estado)
    tickets_cerrados_count = base_query.filter(
        estado__nombre='Cerrado'
    ).count()
    tickets_reparacion_count = base_query.filter(
        estado__nombre='En Reparación'
    ).count()
    total_tickets_periodo = base_query.count()

    puntaje = (
        (tickets_cerrados_count * 1) +
        (tickets_reparacion_count * 0.5)
    )
    eficiencia_ponderada = (
        round((puntaje / total_tickets_periodo) * 100, 1)
        if total_tickets_periodo > 0
        else 0
    )

    # Conteo por estado (sobre consulta filtrada)
    conteo_por_estado = tickets_query.values('estado__nombre').annotate(
        total=Count('id')
    ).order_by()

    # Conteo por turno y estado
    conteo_turno_estado = tickets_query.exclude(
        turno__isnull=True
    ).exclude(
        turno=''
    ).values(
        'turno', 'estado__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('turno')

    labels_turnos = sorted(
        list(tickets_query.exclude(turno__isnull=True).exclude(
            turno=''
        ).values_list('turno', flat=True).distinct())
    )

    estados = ['Abierto', 'En Reparación', 'Cerrado']
    datasets = []

    for estado in estados:
        data = []
        for turno in labels_turnos:
            conteo = next(
                (
                    item['total'] for item in conteo_turno_estado
                    if item['turno'] == turno and
                    item['estado__nombre'] == estado
                ),
                0
            )
            data.append(conteo)
        datasets.append({
            'label': estado,
            'data': data,
            'backgroundColor': color_map.get(estado, '#CCCCCC')
        })

    # Top 5 herramientas con más fallas
    top_herramientas_fallas = tickets_query.values(
        'herramienta__modelo'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    # Top 5 tickets más antiguos (no cerrados)
    top_tickets_antiguos = Ticket.objects.exclude(
        estado__nombre='Cerrado'
    ).order_by('fecha_creacion')[:5]

    # --- 3. Preparar el contexto completo ---
    contexto_completo = {
        'tickets': tickets_query.order_by('-fecha_creacion'),
        'start_date_value': start_date_str,
        'end_date_value': end_date_str,
        'eficiencia_ponderada': eficiencia_ponderada,
        'top_tickets_antiguos': top_tickets_antiguos,
        'top_herramientas_fallas': top_herramientas_fallas,
        'opciones_estado': TicketEstado.objects.all(),
        'opciones_turno': Ticket.objects.filter(
            turno__isnull=False
        ).values_list('turno', flat=True).distinct(),
        'opciones_fabricante': Herramienta.objects.values_list(
            'fabricante', flat=True
        ).distinct(),
        'graficas_data_json': json.dumps({
            'estado_labels': [
                item['estado__nombre'] for item in conteo_por_estado
            ],
            'estado_data': [item['total'] for item in conteo_por_estado],
            'estado_colors': [
                color_map.get(item['estado__nombre'], '#CCCCCC')
                for item in conteo_por_estado
            ],
            'stacked_bar_labels': labels_turnos,
            'stacked_bar_datasets': datasets,
        })
    }

    # Agregar formularios de estado a cada ticket
    for ticket in contexto_completo['tickets']:
        ticket.form_estado = ActualizarEstadoForm(instance=ticket)

    return render(request, 'tickets/dashboard.html', contexto_completo)


@login_required
def detalles_filtrados_modal(request):
    """
    Vista para mostrar tickets filtrados en un modal.
    Soporta filtros por estado, turno, combinación turno-estado y modelo.
    """
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # Obtenemos los parámetros de la URL
    filtro_tipo = request.GET.get('filtro_tipo')
    filtro_valor = request.GET.get('filtro_valor')
    filtro_valor2 = request.GET.get('filtro_valor2')

    # Reutilizamos los filtros de fecha para consistencia
    end_date_str = request.GET.get(
        'end_date',
        timezone.now().strftime('%Y-%m-%d')
    )
    start_date_str = request.GET.get(
        'start_date',
        (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    )

    start_date = timezone.make_aware(
        datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    )
    end_date = timezone.make_aware(
        datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    ) + datetime.timedelta(days=1)

    tickets_filtrados = Ticket.objects.filter(
        fecha_creacion__range=(start_date, end_date)
    )
    titulo_modal = "Detalle de Tickets"

    # Aplicamos el filtro correspondiente
    if filtro_tipo == 'estado':
        tickets_filtrados = tickets_filtrados.filter(
            estado__nombre=filtro_valor
        )
        titulo_modal = f"Tickets con Estado: {filtro_valor}"

    elif filtro_tipo == 'turno':
        tickets_filtrados = tickets_filtrados.filter(turno=filtro_valor)
        titulo_modal = f"Tickets del {filtro_valor}"

    elif filtro_tipo == 'turno_estado':
        tickets_filtrados = tickets_filtrados.filter(
            turno=filtro_valor,
            estado__nombre=filtro_valor2
        )
        titulo_modal = f"Tickets '{filtro_valor2}' del {filtro_valor}"

    elif filtro_tipo == 'modelo':
        tickets_filtrados = tickets_filtrados.filter(
            herramienta__modelo=filtro_valor
        )
        titulo_modal = f"Tickets para el Modelo: {filtro_valor}"

    contexto = {
        'tickets': tickets_filtrados.order_by('-fecha_creacion'),
        'titulo_modal': titulo_modal
    }
    return render(request, 'partials/modal_detalles_generico.html', contexto)


@login_required
def exportar_tickets_excel(request):
    """
    Exporta los tickets filtrados a un archivo Excel (.xlsx).
    Toma los filtros activos del dashboard.
    """
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # --- 1. Reutilizamos la misma lógica de filtros del dashboard ---
    end_date_str = request.GET.get(
        'end_date',
        timezone.now().strftime('%Y-%m-%d')
    )
    start_date_str = request.GET.get(
        'start_date',
        (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    )
    estado_filtro = request.GET.get('estado')
    turno_filtro = request.GET.get('turno')
    fabricante_filtro = request.GET.get('fabricante')

    start_date = timezone.make_aware(
        datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    )
    end_date = timezone.make_aware(
        datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    ) + datetime.timedelta(days=1)

    tickets_query = Ticket.objects.filter(
        fecha_creacion__range=(start_date, end_date)
    )

    if estado_filtro:
        tickets_query = tickets_query.filter(estado__id=estado_filtro)
    if turno_filtro:
        tickets_query = tickets_query.filter(turno=turno_filtro)
    if fabricante_filtro:
        tickets_query = tickets_query.filter(
            herramienta__fabricante=fabricante_filtro
        )

    # --- 2. Creamos el archivo de Excel en memoria ---
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Reporte de Tickets"

    # Definimos los encabezados de las columnas
    headers = [
        "Folio",
        "Estado",
        "Herramienta (Modelo)",
        "No. Serie",
        "Falla",
        "Comentarios",
        "Creado Por",
        "Fecha Creación",
        "Turno",
        "Ubicación"
    ]
    sheet.append(headers)

    # Damos formato a los encabezados
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # --- 3. Llenamos el archivo con los datos de los tickets ---
    for ticket in tickets_query.order_by('fecha_creacion'):
        ubicacion_str = str(ticket.ubicacion) if ticket.ubicacion else "N/A"

        row = [
            ticket.folio,
            ticket.estado.nombre,
            ticket.herramienta.modelo,
            ticket.herramienta.numero_serie,
            ticket.falla.descripcion if ticket.falla else "N/A",
            ticket.comentarios,
            ticket.creado_por.username,
            timezone.localtime(ticket.fecha_creacion).strftime(
                "%d/%m/%Y %H:%M"
            ),
            ticket.turno,
            ubicacion_str
        ]
        sheet.append(row)

    # Ajustamos el ancho de las columnas
    for column_cells in sheet.columns:
        length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = (
            length + 2
        )

    # --- 4. Preparamos la respuesta HTTP para descargar el archivo ---
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        ),
    )
    filename = f"Reporte_Tickets_{timezone.now().strftime('%Y-%m-%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    workbook.save(response)

    return response