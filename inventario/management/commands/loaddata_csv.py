from django.core.management.base import BaseCommand
import csv
import os
from django.contrib.auth.models import User
from inventario.models import Herramienta, Ubicacion
from usuarios.models import Colaborador

class Command(BaseCommand):
    help = 'Load Herramientas and Colaboradores from CSV files in project root'

    def handle(self, *args, **options):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        herramientas_path = os.path.join(base_dir, 'Herramientas.csv')
        colaboradores_path = os.path.join(base_dir, 'Colaborador.csv')

        if os.path.exists(herramientas_path):
            self.stdout.write(f"Leyendo {herramientas_path}...")
            with open(herramientas_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    # Normalizar claves (quitar espacios, etc si fuera necesario)
                    
                    # Mapeo de campos flexible
                    numero_serie = row.get('NumeroSerie') or row.get('numero_serie') or row.get('Numero_serie')
                    modelo = row.get('Modelo') or row.get('modelo')
                    fabricante = row.get('Fabricante') or row.get('fabricante')
                    tipo = row.get('Tipo') or row.get('tipo')
                    numero_reparacion = row.get('NumeroReparacion') or row.get('numero_reparacion')
                    estado = row.get('Estado') or row.get('estado')
                    ejecucion = row.get('Ejecucion') or row.get('ejecucion') or row.get('Ejecución')
                    ubicacion_str = row.get('Ubicacion') or row.get('ubicacion') or row.get('Ubicación')

                    if numero_serie:
                        # Procesar Ubicación
                        ubicacion_obj = None
                        if ubicacion_str:
                            parts = [p.strip() for p in ubicacion_str.split('/')]
                            if len(parts) >= 1:
                                nave = parts[0]
                                banda = parts[1] if len(parts) > 1 else ''
                                tacto = parts[2] if len(parts) > 2 else ''
                                operacion = parts[3] if len(parts) > 3 else ''
                                
                                ubicacion_obj, _ = Ubicacion.objects.get_or_create(
                                    nave=nave,
                                    banda=banda,
                                    tacto=tacto,
                                    operacion=operacion
                                )

                        Herramienta.objects.update_or_create(
                            numero_serie=numero_serie,
                            defaults={
                                'modelo': modelo,
                                'fabricante': fabricante,
                                'tipo': tipo,
                                'numero_reparacion': numero_reparacion,
                                'estado': estado,
                                'ejecucion': ejecucion,
                                'ubicacion': ubicacion_obj
                            }
                        )
                        count += 1
            self.stdout.write(self.style.SUCCESS(f'{count} Herramientas cargadas/actualizadas desde CSV'))
        else:
            self.stdout.write(self.style.WARNING('Herramientas.csv no encontrado'))

        if os.path.exists(colaboradores_path):
            self.stdout.write(f"Leyendo {colaboradores_path}...")
            with open(colaboradores_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    username = row.get('username') or row.get('Username')
                    first_name = row.get('first_name') or row.get('FirstName')
                    last_name = row.get('last_name') or row.get('LastName')
                    email = row.get('email') or row.get('Email')
                    
                    if username:
                        user, created = User.objects.get_or_create(username=username, defaults={
                            'first_name': first_name or '',
                            'last_name': last_name or '',
                            'email': email or ''
                        })
                        Colaborador.objects.get_or_create(usuario=user)
                        count += 1
            self.stdout.write(self.style.SUCCESS(f'{count} Colaboradores cargados desde CSV'))
        else:
            self.stdout.write(self.style.WARNING('Colaboradores.csv no encontrado'))
