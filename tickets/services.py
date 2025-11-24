# tickets/services.py

import json
import datetime
from django.utils import timezone
from django.db.models import Count, Q
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.http import HttpResponse

from .models import Ticket, TicketEstado, Herramienta
from .constants import TicketStatus, ChartColors

class DashboardService:
    @staticmethod
    def get_filtered_tickets(start_date_str, end_date_str, estado_id=None, turno=None, fabricante=None):
        """
        Returns a queryset of tickets filtered by date range and optional parameters.
        Also returns the start and end date objects.
        """
        start_date = timezone.make_aware(datetime.datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.datetime.strptime(end_date_str, '%Y-%m-%d')) + datetime.timedelta(days=1)
        
        base_query = Ticket.objects.filter(fecha_creacion__range=(start_date, end_date))
        tickets_query = base_query

        if estado_id and str(estado_id).isdigit():
            tickets_query = tickets_query.filter(estado__id=int(estado_id))
        if turno:
            tickets_query = tickets_query.filter(turno=turno)
        if fabricante:
            tickets_query = tickets_query.filter(herramienta__fabricante=fabricante)
            
        return base_query, tickets_query, start_date, end_date

    @staticmethod
    def calculate_efficiency(base_query):
        """
        Calculates the efficiency score based on closed and in-repair tickets.
        """
        tickets_cerrados_count = base_query.filter(estado__nombre=TicketStatus.CERRADO).count()
        tickets_reparacion_count = base_query.filter(estado__nombre=TicketStatus.EN_REPARACION).count()
        total_tickets_periodo = base_query.count()
        
        puntaje = (tickets_cerrados_count * 1) + (tickets_reparacion_count * 0.5)
        eficiencia = round((puntaje / total_tickets_periodo) * 100, 1) if total_tickets_periodo > 0 else 0
        return eficiencia

    @staticmethod
    def get_chart_data(tickets_query):
        """
        Prepares data for dashboard charts.
        """
        # Status Chart
        conteo_por_estado = tickets_query.values('estado__nombre').annotate(total=Count('id')).order_by()
        
        # Shift Chart
        conteo_turno_estado = tickets_query.exclude(turno__isnull=True).exclude(turno='').values('turno', 'estado__nombre').annotate(total=Count('id')).order_by('turno')
        labels_turnos = sorted(list(tickets_query.exclude(turno__isnull=True).exclude(turno='').values_list('turno', flat=True).distinct()))
        
        datasets = []
        for estado in [TicketStatus.ABIERTO, TicketStatus.EN_REPARACION, TicketStatus.CERRADO]:
            data = []
            for turno in labels_turnos:
                conteo = next((item['total'] for item in conteo_turno_estado if item['turno'] == turno and item['estado__nombre'] == estado), 0)
                data.append(conteo)
            
            datasets.append({
                'label': estado, 
                'data': data, 
                'backgroundColor': ChartColors.HEX_MAP.get(estado, ChartColors.DEFAULT_HEX)
            })

        return {
            'estado_labels': [item['estado__nombre'] for item in conteo_por_estado],
            'estado_data': [item['total'] for item in conteo_por_estado],
            'estado_colors': [ChartColors.HEX_MAP.get(item['estado__nombre'], ChartColors.DEFAULT_HEX) for item in conteo_por_estado],
            'stacked_bar_labels': labels_turnos,
            'stacked_bar_datasets': datasets,
        }

    @staticmethod
    def get_top_stats(tickets_query, base_query):
        """
        Returns top failing tools and oldest open tickets.
        """
        top_herramientas = tickets_query.values('herramienta__modelo').annotate(total=Count('id')).order_by('-total')[:5]
        # Oldest tickets should probably be from the whole DB or the filtered range? 
        # Original code used Ticket.objects.exclude... so it was global.
        # But usually dashboard shows stats for the period or global backlog?
        # Let's stick to original logic: Ticket.objects.exclude(estado__nombre='Cerrado')
        top_antiguos = Ticket.objects.exclude(estado__nombre=TicketStatus.CERRADO).order_by('fecha_creacion')[:5]
        
        return top_herramientas, top_antiguos

    @staticmethod
    def generate_excel_report(tickets_query):
        """
        Generates an Excel file from the tickets query.
        """
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Reporte de Tickets"

        headers = [
            "Folio", "Estado", "Herramienta (Modelo)", "No. Serie", "Falla",
            "Comentarios", "Creado Por", "Fecha Creación", "Turno", "Ubicación"
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")

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
                timezone.localtime(ticket.fecha_creacion).strftime("%d/%m/%Y %H:%M"),
                ticket.turno,
                ubicacion_str
            ]
            sheet.append(row)

        for column_cells in sheet.columns:
            length = max(len(str(cell.value or "")) for cell in column_cells)
            sheet.column_dimensions[column_cells[0].column_letter].width = length + 2

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f"Reporte_Tickets_{timezone.now().strftime('%Y-%m-%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        workbook.save(response)
        
        return response
