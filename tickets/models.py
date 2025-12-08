# tickets/models.py
"""
Modelos para el sistema de tickets de reparación.
Optimizado con índices de base de datos para mejor rendimiento.
"""

from django.db import models
from django.contrib.auth.models import User
from inventario.models import Herramienta, Ubicacion


class Falla(models.Model):
    """Catálogo de fallas comunes en herramientas."""
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255)
    posible_causa = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    class Meta:
        verbose_name = 'Falla'
        verbose_name_plural = 'Fallas'


class TicketEstado(models.Model):
    """Estados posibles de un ticket (Abierto, En Reparación, Cerrado)."""
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Estado de Ticket'
        verbose_name_plural = 'Estados de Ticket'


class Ticket(models.Model):
    """Ticket de reparación de herramienta."""
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
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['-fecha_creacion'], name='ticket_fecha_idx'),
            models.Index(fields=['estado', '-fecha_creacion'], name='ticket_estado_fecha_idx'),
            models.Index(fields=['herramienta'], name='ticket_herramienta_idx'),
            models.Index(fields=['creado_por', '-fecha_creacion'], name='ticket_usuario_idx'),
            models.Index(fields=['folio'], name='ticket_folio_idx'),
        ]


class AuditoriaTicket(models.Model):
    """Registro de auditoría para cambios en tickets."""
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
        verbose_name = 'Auditoría de Ticket'
        verbose_name_plural = 'Auditorías de Tickets'
        indexes = [
            models.Index(fields=['ticket', '-fecha'], name='audit_ticket_fecha_idx'),
        ]


class Notificacion(models.Model):
    """Notificaciones para usuarios sobre cambios en tickets."""
    usuario_destino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mensaje

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['usuario_destino', 'leido', '-fecha_creacion'], 
                        name='notif_usuario_leido_idx'),
            models.Index(fields=['ticket'], name='notif_ticket_idx'),
        ]


class Comentario(models.Model):
    """Comentarios en el historial de un ticket."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='historial_comentarios')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor.username if self.autor else 'Usuario eliminado'} en ticket {self.ticket.folio}"

    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        indexes = [
            models.Index(fields=['ticket', 'fecha_creacion'], name='comment_ticket_fecha_idx'),
        ]