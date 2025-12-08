import time
from django.core.management.base import BaseCommand
from inventario.models import Ubicacion

class Command(BaseCommand):
    help = 'Puebla la base de datos con las ubicaciones predefinidas para las naves A60 y A40/41'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando la carga de ubicaciones ---'))
        
        start_time = time.time()
        total_creadas = 0

        # --- Definición de Ubicaciones ---

        # 1. Ubicaciones para la Nave A60
        nave_a60 = 'A60'
        bandas_a60 = ['0a', '0b', '1', '2', '3', '4', '5', '6', '7', 'TMF', 'CMF', 'EBV', 'TW', 'AT']
        # Asumimos que cada banda tiene tactos del 1 al 20. Puedes ajustar este número.
        rango_tactos = range(1, 21) 

        self.stdout.write(f"Creando ubicaciones para la nave {nave_a60}...")
        creadas_a60 = 0
        for banda in bandas_a60:
            for tacto_num in rango_tactos:
                tacto = str(tacto_num)
                # get_or_create evita crear duplicados si el script se ejecuta de nuevo
                obj, created = Ubicacion.objects.get_or_create(
                    nave=nave_a60,
                    banda=banda,
                    tacto=tacto
                )
                if created:
                    creadas_a60 += 1
        total_creadas += creadas_a60
        self.stdout.write(self.style.SUCCESS(f'OK. {creadas_a60} nuevas ubicaciones creadas para A60.'))


        # 2. Ubicaciones para la Nave A40/41 (Anbau)
        nave_a40_41 = 'A40/41'
        banda_anbau = 'Anbau'
        # Operaciones desde la 10 hasta la 140
        rango_operaciones = range(10, 141)

        self.stdout.write(f"Creando ubicaciones para la nave {nave_a40_41}...")
        creadas_a40 = 0
        for op_num in rango_operaciones:
            operacion = str(op_num)
            obj, created = Ubicacion.objects.get_or_create(
                nave=nave_a40_41,
                banda=banda_anbau,
                operacion=operacion
            )
            if created:
                creadas_a40 += 1
        total_creadas += creadas_a40
        self.stdout.write(self.style.SUCCESS(f'OK. {creadas_a40} nuevas ubicaciones creadas para A40/41.'))

        # --- Finalización ---
        end_time = time.time()
        duracion = round(end_time - start_time, 2)

        self.stdout.write(self.style.SUCCESS('-----------------------------------------'))
        self.stdout.write(self.style.SUCCESS(f'¡Proceso completado en {duracion} segundos!'))
        self.stdout.write(self.style.SUCCESS(f'Total de nuevas ubicaciones creadas: {total_creadas}'))