# tickets/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group # <-- Añade Group a la importación
from .models import Ticket, Notificacion

@receiver(post_save, sender=Ticket)
def crear_notificacion_nuevo_ticket(sender, instance, created, **kwargs):
    """
    Señal que se activa después de que se guarda un ticket para crear notificaciones.
    Ahora notifica a los miembros del grupo 'Service Line'.
    """
    if created:
        try:
            # 1. Buscamos el grupo específico por su nombre
            service_line_group = Group.objects.get(name='Service Line')
            # 2. Obtenemos todos los usuarios que pertenecen a ese grupo
            usuarios_a_notificar = service_line_group.user_set.all()

            print(f"Señal activada para ticket {instance.folio}. Grupo 'Service Line' encontrado con {usuarios_a_notificar.count()} usuarios.")

            for usuario in usuarios_a_notificar:
                if usuario != instance.creado_por:
                    mensaje = f"Nuevo ticket {instance.folio} creado por {instance.creado_por.username}."
                    Notificacion.objects.create(
                        usuario_destino=usuario,
                        ticket=instance,
                        mensaje=mensaje
                    )
                    print(f"Notificación creada para {usuario.username}.")

        except Group.DoesNotExist:
            # Este mensaje aparecerá si el grupo 'Service Line' no existe
            print("ADVERTENCIA: El grupo 'Service Line' no existe. No se pueden crear notificaciones.")