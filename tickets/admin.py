# tickets/admin.py

from django.contrib import admin
from .models import Falla, TicketEstado, Ticket, AuditoriaTicket, Notificacion

# Registramos todos los modelos de la app tickets.
admin.site.register(Falla)
admin.site.register(TicketEstado)
admin.site.register(Ticket)
admin.site.register(AuditoriaTicket)
admin.site.register(Notificacion)