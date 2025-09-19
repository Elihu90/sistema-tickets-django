# tickets/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Ticket, Notificacion

@receiver(post_save, sender=Ticket)
def crear_notificacion_nuevo_ticket(sender, instance, created, **kwargs):
    """
    Señal que se activa después de que se guarda un ticket para crear notificaciones.
    """
    # 'created' es True solo si el ticket es nuevo.
    if created:
        # Buscamos a todos los usuarios que son 'staff' (administradores).
        usuarios_a_notificar = User.objects.filter(is_staff=True)
        
        print(f"Señal activada para el ticket {instance.folio}. Se encontraron {usuarios_a_notificar.count()} usuarios staff.")

        for usuario in usuarios_a_notificar:
            # Evitamos notificar al usuario que creó el ticket
            if usuario != instance.creado_por:
                mensaje = f"Nuevo ticket {instance.folio} creado por {instance.creado_por.username}."
                Notificacion.objects.create(
                    usuario_destino=usuario,
                    ticket=instance,
                    mensaje=mensaje
                )
                print(f"Notificación creada para {usuario.username}.")