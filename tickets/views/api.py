# tickets/views/api.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from tickets.models import Ticket, Herramienta
from tickets.forms import ActualizarEstadoForm
from tickets.constants import TicketStatus

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


def verificar_ticket_duplicado(request, herramienta_pk):
    """
    Vista para HTMX: Busca tickets abiertos o en reparación para una herramienta específica.
    """
    # Buscamos tickets para esa herramienta cuyo estado NO sea 'Cerrado'
    tickets_abiertos = Ticket.objects.filter(
        herramienta_id=herramienta_pk
    ).exclude(
        estado__nombre=TicketStatus.CERRADO
    )

    contexto = {
        'tickets_duplicados': tickets_abiertos
    }
    # Renderiza la plantilla parcial que mostrará la advertencia
    return render(request, 'partials/advertencia_duplicado.html', contexto)
