# tickets/views/dashboard.py

import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from tickets.models import Ticket, TicketEstado, Herramienta
from tickets.forms import ActualizarEstadoForm
from tickets.services import DashboardService

@login_required
def dashboard_service_line(request):
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # --- 1. Recopilar filtros ---
    end_date_str = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
    start_date_str = request.GET.get('start_date', (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
    estado_filtro = request.GET.get('estado')
    turno_filtro = request.GET.get('turno')
    fabricante_filtro = request.GET.get('fabricante')

    # --- 2. Usar el servicio para obtener datos ---
    base_query, tickets_query, start_date, end_date = DashboardService.get_filtered_tickets(
        start_date_str, end_date_str, estado_filtro, turno_filtro, fabricante_filtro
    )

    # --- 3. Calcular estadísticas ---
    eficiencia_ponderada = DashboardService.calculate_efficiency(base_query)
    chart_data = DashboardService.get_chart_data(tickets_query)
    top_herramientas_fallas, top_tickets_antiguos = DashboardService.get_top_stats(tickets_query, base_query)

    # --- 4. Preparar el contexto completo para la plantilla ---
    contexto_completo = {
        'tickets': tickets_query.order_by('-fecha_creacion'),
        'start_date_value': start_date_str, 'end_date_value': end_date_str,
        'eficiencia_ponderada': eficiencia_ponderada,
        'top_tickets_antiguos': top_tickets_antiguos,
        'top_herramientas_fallas': top_herramientas_fallas,
        'opciones_estado': TicketEstado.objects.all(),
        'opciones_turno': Ticket.objects.filter(turno__isnull=False).values_list('turno', flat=True).distinct(),
        'opciones_fabricante': Herramienta.objects.values_list('fabricante', flat=True).distinct(),
        'contexto_graficas': chart_data
    }

    for ticket in contexto_completo['tickets']:
        ticket.form_estado = ActualizarEstadoForm(instance=ticket)
    
    return render(request, 'tickets/dashboard.html', contexto_completo)


@login_required
def ticket_estado_data(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    # This view seems redundant if dashboard_service_line passes all data, 
    # but keeping it for compatibility if frontend fetches it asynchronously.
    # However, the original view logic was simpler and didn't use filters from request?
    # Let's check original logic. It was just global count.
    
    # Re-implementing original logic but using Service if possible, or just simple query.
    # The original view didn't take filters.
    
    from django.db.models import Count
    from tickets.constants import ChartColors
    
    conteo = Ticket.objects.values('estado__nombre').annotate(total=Count('id'))
    
    labels = [item['estado__nombre'] for item in conteo]
    data = [item['total'] for item in conteo]
    background_colors = [ChartColors.RGBA_MAP.get(label, ChartColors.DEFAULT_HEX) for label in labels]

    return JsonResponse({
        'labels': labels,
        'data': data,
        'colors': background_colors,
    })


@login_required
def exportar_tickets_excel(request):
    """
    Toma los filtros activos del dashboard, consulta la base de datos
    y genera un archivo .xlsx para descargar.
    """
    if not request.user.is_staff:
        return redirect('lista_tickets')

    end_date_str = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
    start_date_str = request.GET.get('start_date', (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
    estado_filtro = request.GET.get('estado')
    turno_filtro = request.GET.get('turno')
    fabricante_filtro = request.GET.get('fabricante')

    _, tickets_query, _, _ = DashboardService.get_filtered_tickets(
        start_date_str, end_date_str, estado_filtro, turno_filtro, fabricante_filtro
    )

    return DashboardService.generate_excel_report(tickets_query)


@login_required
def detalles_filtrados_modal(request):
    if not request.user.is_staff:
        return redirect('lista_tickets')

    # Obtenemos los parámetros de la URL
    filtro_tipo = request.GET.get('filtro_tipo')
    filtro_valor = request.GET.get('filtro_valor')
    filtro_valor2 = request.GET.get('filtro_valor2') 

    end_date_str = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
    start_date_str = request.GET.get('start_date', (timezone.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))
    
    # We can reuse get_filtered_tickets partially or just manual filter as before
    # Since this has specific logic for modal types, let's keep it similar but cleaner.
    
    start_date = timezone.make_aware(datetime.datetime.strptime(start_date_str, '%Y-%m-%d'))
    end_date = timezone.make_aware(datetime.datetime.strptime(end_date_str, '%Y-%m-%d')) + datetime.timedelta(days=1)
    
    tickets_filtrados = Ticket.objects.filter(fecha_creacion__range=(start_date, end_date))
    titulo_modal = "Detalle de Tickets"

    if filtro_tipo == 'estado':
        tickets_filtrados = tickets_filtrados.filter(estado__nombre=filtro_valor)
        titulo_modal = f"Tickets con Estado: {filtro_valor}"
    
    elif filtro_tipo == 'turno':
        tickets_filtrados = tickets_filtrados.filter(turno=filtro_valor)
        titulo_modal = f"Tickets del {filtro_valor}"

    elif filtro_tipo == 'turno_estado':
        tickets_filtrados = tickets_filtrados.filter(turno=filtro_valor, estado__nombre=filtro_valor2)
        titulo_modal = f"Tickets '{filtro_valor2}' del {filtro_valor}"

    elif filtro_tipo == 'modelo':
        tickets_filtrados = tickets_filtrados.filter(herramienta__modelo=filtro_valor)
        titulo_modal = f"Tickets para el Modelo: {filtro_valor}"

    contexto = {
        'tickets': tickets_filtrados.order_by('-fecha_creacion'),
        'titulo_modal': titulo_modal
    }
    return render(request, 'partials/modal_detalles_generico.html', contexto)
