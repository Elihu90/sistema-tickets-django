# inventario/management/commands/import_herramientas.py

import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from inventario.models import Herramienta

class Command(BaseCommand):
    help = 'Carga datos de herramientas desde un archivo CSV'

    def handle(self, *args, **kwargs):
        # Ruta al archivo CSV que movimos a la raíz del proyecto
        ruta_archivo = settings.BASE_DIR / 'herramientas.csv'
        self.stdout.write(self.style.SUCCESS(f'Iniciando la carga desde {ruta_archivo}'))

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8-sig') as archivo_csv:
                # Usamos DictReader para leer el CSV como un diccionario
                lector_csv = csv.DictReader(archivo_csv)
                
                contador_creados = 0
                contador_actualizados = 0

                for fila in lector_csv:
                    # Usamos get_or_create para evitar duplicados basados en el número de serie
                    # Si la herramienta ya existe, la obtiene; si no, la crea.
                    herramienta, creado = Herramienta.objects.get_or_create(
                        numero_serie=fila['NumeroSerie'],
                        defaults={
                            'numero_reparacion': fila['NumeroReparacion'],
                            'fabricante': fila['Fabricante'],
                            'modelo': fila['Modelo'],
                            'tipo': fila['Tipo'],
                            'ejecucion': fila['Ejecución'],
                            'estado': fila['Estado']
                        }
                    )

                    if creado:
                        contador_creados += 1
                        self.stdout.write(self.style.SUCCESS(f'Creada: {herramienta}'))
                    else:
                        # Opcional: podrías actualizar los datos si la herramienta ya existe
                        contador_actualizados += 1
                
                self.stdout.write(self.style.SUCCESS(f'\nProceso completado.'))
                self.stdout.write(self.style.SUCCESS(f'{contador_creados} herramientas creadas.'))
                self.stdout.write(self.style.WARNING(f'{contador_actualizados} herramientas ya existían.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Error: El archivo herramientas.csv no se encontró en la raíz del proyecto.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error inesperado: {e}'))