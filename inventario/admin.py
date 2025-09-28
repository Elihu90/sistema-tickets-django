# inventario/admin.py

from django.contrib import admin
from .models import Ubicacion, Herramienta

# Registramos los modelos de la app inventario.
admin.site.register(Ubicacion)
admin.site.register(Herramienta)