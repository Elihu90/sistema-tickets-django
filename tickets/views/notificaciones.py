# tickets/views/notificaciones.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from tickets.models import Notificacion

@login_required
def ver_notificaciones(request: HttpRequest) -> HttpResponse:
    """
    Muestra las notificaciones sin leer del usuario.
    """
    notificaciones = Notificacion.objects.filter(usuario_destino=request.user, leido=False)
    return render(request, 'partials/lista_notificaciones.html', {'notificaciones': notificaciones})


@login_required
def contar_notificaciones_sin_leer(request: HttpRequest) -> HttpResponse:
    cantidad = Notificacion.objects.filter(usuario_destino=request.user, leido=False).count()
    return render(request, 'partials/contador_notificaciones.html', {'cantidad_notificaciones': cantidad})


@login_required
def marcar_leida_y_redirigir(request: HttpRequest, notificacion_pk: int) -> HttpResponse:
    """
    Marca una notificación como leída y redirige al ticket asociado.
    """
    notificacion = get_object_or_404(Notificacion, pk=notificacion_pk, usuario_destino=request.user)
    notificacion.leido = True
    notificacion.save()
    return redirect('detalles_ticket', pk=notificacion.ticket.pk)
