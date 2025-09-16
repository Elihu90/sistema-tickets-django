# tickets/views.py

# tickets/views.py

from django.shortcuts import render, redirect
from django.contrib import messages  # <-- Importamos los mensajes
from django.contrib.auth.decorators import login_required
from .forms import TicketForm
from .models import TicketEstado
from .models import Herramienta
from .models import Ticket
import datetime
from django.contrib.auth.decorators import login_required
@login_required


def crear_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                # Intentamos obtener el estado "Abierto"
                estado_abierto = TicketEstado.objects.get(nombre='Abierto')

                nuevo_ticket = form.save(commit=False)
                
                nuevo_ticket.estado = estado_abierto
                nuevo_ticket.creado_por = request.user
                
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                nuevo_ticket.folio = f'FOLIO-{timestamp}'
                
                nuevo_ticket.save()

                # Añadimos un mensaje de éxito
                messages.success(request, f"¡Ticket {nuevo_ticket.folio} creado exitosamente!")
                
                return redirect('crear_ticket')

            except TicketEstado.DoesNotExist:
                # Si no existe, mostramos un error amigable en lugar de crashear
                messages.error(request, "Error crítico: El estado 'Abierto' no existe. Por favor, créalo en el panel de administración.")
    
    else: # Método GET
        form = TicketForm()
        
    contexto = {'form': form}
    return render(request, 'tickets/crear_ticket.html', contexto)

def buscar_herramientas(request):
    # Toma el texto de búsqueda enviado por HTMX
    query = request.POST.get('text_search')
    # Busca herramientas que coincidan en el número de serie o modelo
    herramientas = Herramienta.objects.filter(numero_serie__icontains=query) | Herramienta.objects.filter(modelo__icontains=query)
    # Renderiza una plantilla "parcial" con los resultados
    return render(request, 'tickets/partials/search_results.html', {'herramientas': herramientas})

def detalles_herramienta(request, pk):
    # Obtiene la herramienta específica por su ID (pk)
    herramienta = Herramienta.objects.get(pk=pk)
    # Renderiza una plantilla "parcial" con los detalles
    return render(request, 'tickets/partials/herramienta_details.html', {'herramienta': herramienta})

def lista_tickets(request):
    # El nombre de la función debe ser exactamente este
    tickets_del_usuario = Ticket.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
    
    contexto = {
        'tickets': tickets_del_usuario
    }
    return render(request, 'tickets/lista_tickets.html', contexto)