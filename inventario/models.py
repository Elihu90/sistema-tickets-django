# inventario/models.py

from django.db import models

class Ubicacion(models.Model):
    class TipoUbicacion(models.TextChoices):
        NAVE = 'NAVE', 'Nave'
        BANDA = 'BANDA', 'Banda'
        TACTO = 'TACTO', 'Tacto'

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TipoUbicacion.choices)
    id_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ubicación Padre')

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

class Herramienta(models.Model):
    numero_serie = models.CharField(max_length=100, unique=True)
    numero_reparacion = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    ejecucion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.modelo or 'N/A'} - S/N: {self.numero_serie}"

    class Meta:
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'