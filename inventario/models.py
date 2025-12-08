# inventario/models.py
"""
Modelos para el inventario de herramientas y ubicaciones.
Optimizado con índices de base de datos.
"""

from django.db import models


class Ubicacion(models.Model):
    """Ubicación física de una herramienta en la planta."""
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
        indexes = [
            models.Index(fields=['nave', 'banda'], name='ubicacion_nave_banda_idx'),
        ]


class Herramienta(models.Model):
    """Herramienta del inventario."""
    numero_serie = models.CharField(max_length=100, unique=True, db_index=True)
    numero_reparacion = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    modelo = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    ejecucion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    # Relación con la ubicación
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.modelo or 'N/A'} - S/N: {self.numero_serie}"

    class Meta:
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'
        indexes = [
            models.Index(fields=['fabricante', 'modelo'], name='herramienta_fab_modelo_idx'),
            models.Index(fields=['ubicacion'], name='herramienta_ubicacion_idx'),
        ]


class Refaccion(models.Model):
    """Catálogo de refacciones con número SAP."""
    numero_sap = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Número SAP")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    cantidad = models.IntegerField(default=0, verbose_name="Cantidad en Stock")
    ubicacion_almacen = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación en Almacén")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio Unitario")
    proveedor = models.CharField(max_length=150, blank=True, null=True, verbose_name="Proveedor")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    imagen = models.ImageField(upload_to='refacciones/', blank=True, null=True, verbose_name="Imagen/Fotografía")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    def __str__(self):
        return f"{self.numero_sap} - {self.descripcion}"

    class Meta:
        verbose_name = 'Refacción'
        verbose_name_plural = 'Refacciones'
        ordering = ['numero_sap']
        indexes = [
            models.Index(fields=['numero_sap'], name='refaccion_sap_idx'),
            models.Index(fields=['descripcion'], name='refaccion_desc_idx'),
        ]
