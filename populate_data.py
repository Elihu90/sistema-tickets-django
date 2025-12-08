# populate_data.py
"""Script to populate the Django app with sample data.
Genera fallas aleatorias y tickets desde el 1 de octubre de 2025 hasta hoy.
"""
import os
import django
import random
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgtr.settings')
django.setup()

from tickets.models import Falla, Ticket, TicketEstado, Comentario, Notificacion
from inventario.models import Herramienta, Ubicacion
from usuarios.models import Colaborador, GrupoNotificacion
from tickets.constants import Turno, TicketStatus

def create_fallas(num=10):
    for i in range(num):
        codigo = f"F{i+1:03d}"
        descripcion = f"Falla simulada {i+1}"
        posible_causa = f"Causa posible {i+1}"
        Falla.objects.get_or_create(codigo=codigo, defaults={
            'descripcion': descripcion,
            'posible_causa': posible_causa,
        })
    print(f"Created {num} fallas.")

def create_herramientas(num=20):
    for i in range(num):
        modelo = f"Modelo-{i+1}"
        numero_serie = f"SN{i+1000}"
        fabricante = random.choice(['Acme', 'Globex', 'Initech'])
        Herramienta.objects.get_or_create(numero_serie=numero_serie, defaults={
            'modelo': modelo,
            'fabricante': fabricante,
        })
    print(f"Created {num} herramientas.")

def create_ubicaciones(num=5):
    for i in range(num):
        banda = f"Banda-{i+1}"
        Ubicacion.objects.get_or_create(banda=banda)
    print(f"Created {num} ubicaciones.")

def create_grupos_notificacion():
    grupos = ['Mantenimiento', 'Líderes de Línea']
    for nombre in grupos:
        GrupoNotificacion.objects.get_or_create(nombre=nombre)
    print("Created grupos de notificación.")

def create_colaboradores(num=10):
    from django.contrib.auth.models import User
    for i in range(num):
        username = f"user{i+1}"
        user, _ = User.objects.get_or_create(username=username, defaults={
            'first_name': f"User{i+1}",
            'last_name': 'Test',
            'email': f"user{i+1}@example.com",
        })
        Colaborador.objects.get_or_create(usuario=user)
    print(f"Created {num} colaboradores.")

def create_ticket_estados():
    estados = ['Abierto', 'En Reparación', 'Cerrado']
    for nombre in estados:
        TicketEstado.objects.get_or_create(nombre=nombre)
    print("Ticket estados ensured.")

def random_date(start, end):
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + datetime.timedelta(seconds=random_seconds)

def create_tickets(num=100):
    estados = list(TicketEstado.objects.all())
    herramientas = list(Herramienta.objects.all())
    fallas = list(Falla.objects.all())
    ubicaciones = list(Ubicacion.objects.all())
    colaboradores = list(Colaborador.objects.all())
    start_date = timezone.make_aware(datetime.datetime(2025, 10, 1))
    end_date = timezone.now()
    for i in range(num):
        fecha = random_date(start_date, end_date)
        turno = random.choice([Turno.PRIMERO, Turno.SEGUNDO, Turno.TERCERO])
        creador = random.choice(colaboradores).usuario
        herramienta = random.choice(herramientas)
        falla = random.choice(fallas) if random.random() < 0.5 else None
        ubicacion = random.choice(ubicaciones)
        estado = random.choice(estados)
        ticket = Ticket.objects.create(
            folio=f"TK{1000+i}",
            numero_ticket_externo=None,
            comentarios='Generado automáticamente',
            fecha_creacion=fecha,
            fecha_actualizacion=fecha,
            creado_por=creador,
            herramienta=herramienta,
            falla=falla,
            ubicacion=ubicacion,
            estado=estado,
            turno=turno,
        )
    print(f"Created {num} tickets.")

if __name__ == '__main__':
    create_fallas()
    create_herramientas()
    create_ubicaciones()
    create_grupos_notificacion()
    create_colaboradores()
    create_ticket_estados()
    create_tickets()
    print('Data population complete.')
