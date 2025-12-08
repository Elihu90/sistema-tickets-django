# usuarios/management/commands/import_colaboradores.py

import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from usuarios.models import Colaborador
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Carga datos de colaboradores desde un archivo CSV'

    def handle(self, *args, **kwargs):
        ruta_archivo = settings.BASE_DIR / 'Colaborador.csv'
        self.stdout.write(self.style.SUCCESS(f'Iniciando carga desde {ruta_archivo}'))

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8-sig') as archivo_csv:
                lector_csv = csv.DictReader(archivo_csv)
                
                for fila in lector_csv:
                    email = fila.get('CorreoElectronico')
                    if not email:
                        self.stdout.write(self.style.WARNING(f"Saltando fila sin correo electrónico: {fila['Nombre']}"))
                        continue

                    # 1. Generar un nombre de usuario desde el email
                    username = email.split('@')[0]

                    # 2. Dividir el nombre completo en nombre y apellido
                    nombre_completo = fila['Nombre'].split()
                    first_name = nombre_completo[0] if nombre_completo else ''
                    last_name = ' '.join(nombre_completo[1:]) if len(nombre_completo) > 1 else ''

                    try:
                        # 3. Crear o obtener el objeto User
                        user, creado = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'first_name': first_name,
                                'last_name': last_name,
                                'email': email,
                            }
                        )

                        if creado:
                            # 4. Asignar una contraseña inutilizable por seguridad
                            user.set_unusable_password()
                            user.save()
                            self.stdout.write(self.style.SUCCESS(f'Usuario "{user.username}" creado.'))
                        
                        # 5. Crear o actualizar el perfil de Colaborador asociado
                        Colaborador.objects.update_or_create(
                            usuario=user,
                            defaults={'puesto': fila['Puesto']}
                        )

                    except IntegrityError:
                        self.stdout.write(self.style.WARNING(f'Usuario con email "{email}" o username "{username}" ya existe. Saltando.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error procesando a "{fila["Nombre"]}": {e}'))

            self.stdout.write(self.style.SUCCESS('\nProceso de carga de colaboradores completado.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: El archivo {ruta_archivo.name} no se encontró.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error inesperado: {e}'))