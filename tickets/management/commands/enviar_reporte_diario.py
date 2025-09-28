# tickets/management/commands/enviar_reporte_diario.py

import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from tickets.models import Ticket

class Command(BaseCommand):
    help = 'Recopila los tickets creados en las últimas 24 horas y envía un reporte por correo.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando la recopilación de tickets para el reporte diario...")
        
        ahora = timezone.now()
        hace_24_horas = ahora - datetime.timedelta(hours=24)
        
        tickets_recientes = Ticket.objects.filter(fecha_creacion__range=(hace_24_horas, ahora))

        if not tickets_recientes.exists():
            self.stdout.write(self.style.SUCCESS("No se encontraron tickets nuevos. No se enviará correo."))
            return

        self.stdout.write(f"Se encontraron {tickets_recientes.count()} tickets nuevos.")

        asunto = f"Reporte Diario de Tickets - {ahora.strftime('%d/%m/%Y')}"
        destinatarios = ['serviceline@ejemplo.com'] 
        contexto = {
            'tickets': tickets_recientes,
            'fecha_reporte': ahora,
        }
        
        cuerpo_html = render_to_string('emails/reporte_diario.html', contexto)
        
        send_mail(
            subject=asunto,
            message='',
            from_email='sistema-tickets@tu-empresa.com',
            recipient_list=destinatarios,
            html_message=cuerpo_html,
        )

        self.stdout.write(self.style.SUCCESS(f"Reporte diario enviado exitosamente a {', '.join(destinatarios)}."))