# inventario/models.py

from django.db import models

# Modelo Ubicacion con la nueva estructura de campos separados
class Ubicacion(models.Model):
    nave = models.CharField(max_length=50, blank=True, null=True)
    banda = models.CharField(max_length=50, blank=True, null=True)
    tacto = models.CharField(max_length=50, blank=True, null=True)
    operacion = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de Operación")

    def __str__(self):
        # Crea un nombre legible como "A60 / 0a / 1"
        parts = [self.nave, self.banda, self.tacto, self.operacion]
        return " / ".join(part for part in parts if part)

    class Meta:
        # Evita que se creen ubicaciones duplicadas
        unique_together = ('nave', 'banda', 'tacto', 'operacion')
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

# Tu modelo Herramienta, con la relación a la nueva Ubicacion
class Herramienta(models.Model):
    numero_serie = models.CharField(max_length=100, unique=True)
    numero_reparacion = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    ejecucion = models.CharField(max_length=100, blank=True, null=True)
    
    # Añadimos la relación con la ubicación
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.modelo or 'N/A'} - S/N: {self.numero_serie}"

    class Meta:
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'