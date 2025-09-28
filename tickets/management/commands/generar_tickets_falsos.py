import random
import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import Ticket, Falla, TicketEstado
from inventario.models import Herramienta, Ubicacion

class Command(BaseCommand):
    help = 'Genera 200 tickets falsos (CON TURNOS) para pruebas.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando la generación de 200 tickets de prueba ---'))

        # Verificamos que existan los datos necesarios
        required_models = [User, Herramienta, Ubicacion]
        model_names = ['Usuarios', 'Herramientas', 'Ubicaciones']
        for model, name in zip(required_models, model_names):
            if not model.objects.exists():
                self.stdout.write(self.style.ERROR(f'Error: Se necesitan {name} en la BBDD.'))
                return

        self.stdout.write('Verificando datos base (Fallas y Estados)...')
        # ... (La creación de Fallas y Estados se queda igual) ...
        fallas_base = [('F01', 'No enciende'), ('F02', 'Ruido extraño'), ('F03', 'Intermitente')]
        for codigo, descripcion in fallas_base:
            Falla.objects.get_or_create(codigo=codigo, defaults={'descripcion': descripcion})
        TicketEstado.objects.get_or_create(nombre='Abierto')
        TicketEstado.objects.get_or_create(nombre='En Reparación')
        TicketEstado.objects.get_or_create(nombre='Cerrado')

        # Obtenemos las listas de objetos
        usuarios = list(User.objects.all())
        herramientas = list(Herramienta.objects.all())
        ubicaciones = list(Ubicacion.objects.all())
        fallas = list(Falla.objects.all())
        estados = list(TicketEstado.objects.all())
        
        # ⭐ Definimos los posibles turnos que asignaremos aleatoriamente
        turnos_posibles = ["1er Turno", "2do Turno", "3er Turno"]

        self.stdout.write('Generando 200 tickets...')
        # Primero, borramos los tickets falsos anteriores para no acumularlos
        Ticket.objects.filter(folio__startswith='TEST-').delete()
        
        tickets_creados = 0
        for i in range(200):
            herramienta_aleatoria = random.choice(herramientas)
            usuario_aleatorio = random.choice(usuarios)
            falla_aleatoria = random.choice(fallas)
            estado_aleatorio = random.choice(estados)
            ubicacion_aleatoria = herramienta_aleatoria.ubicacion or random.choice(ubicaciones)
            turno_aleatorio = random.choice(turnos_posibles) # Elegimos un turno al azar
            folio_unico = f"TEST-{int(time.time() * 1000)}-{i}"

            Ticket.objects.create(
                folio=folio_unico,
                herramienta=herramienta_aleatoria,
                ubicacion=ubicacion_aleatoria,
                creado_por=usuario_aleatorio,
                estado=estado_aleatorio,
                falla=falla_aleatoria,
                comentarios=f'Comentario de prueba para el ticket falso #{i+1}.',
                turno=turno_aleatorio # <-- ¡Aquí asignamos el turno!
            )
            tickets_creados += 1
            self.stdout.write('.', ending='')
            self.stdout.flush()
        
        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(f'--- ¡Proceso completado! Se generaron {tickets_creados} tickets nuevos. ---'))