# usuarios/models.py

from django.db import models
from django.contrib.auth.models import User

class Colaborador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        
# ... (modelo Colaborador) ...

class GrupoNotificacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Mantenimiento, Líderes de Línea")
    miembros = models.ManyToManyField(Colaborador, related_name="grupos_notificacion")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo de Notificación'
        verbose_name_plural = 'Grupos de Notificación'