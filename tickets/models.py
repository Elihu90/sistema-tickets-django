# tickets/models.py

from django.db import models
from django.contrib.auth.models import User
from inventario.models import Herramienta, Ubicacion

class Falla(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255)
    posible_causa = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    class Meta:
        verbose_name = 'Falla'
        verbose_name_plural = 'Fallas'

class TicketEstado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Estado de Ticket'
        verbose_name_plural = 'Estados de Ticket'

class Ticket(models.Model):
    folio = models.CharField(max_length=50, unique=True)
    numero_ticket_externo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='tickets_creados')
    herramienta = models.ForeignKey(Herramienta, on_delete=models.PROTECT)
    falla = models.ForeignKey(Falla, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT)
    estado = models.ForeignKey(TicketEstado, on_delete=models.PROTECT)
    turno = models.CharField(max_length=50, blank=True, null=True, verbose_name="Turno")


    def __str__(self):
        return f"Ticket {self.folio} ({self.estado.nombre})"

class AuditoriaTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    campo_modificado = models.CharField(max_length=50, blank=True, null=True)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    tacto = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tacto")
    operacion = models.CharField(max_length=50, blank=True, null=True, verbose_name="Operación")

    def __str__(self):
        return f"Auditoría {self.id} en Ticket {self.ticket.folio}"

    class Meta:
        ordering = ['-fecha']