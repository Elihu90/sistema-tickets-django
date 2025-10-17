"""
Módulo de formularios para la aplicación 'tickets'.

Define los formularios utilizados para la creación, edición y gestión de
tickets, así como para la adición de comentarios y la actualización de estados.
Este módulo integra 'django-crispy-forms' para un renderizado avanzado
y utiliza HTMX para interacciones dinámicas en el frontend.
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, HTML, Layout, Row, Submit
from django import forms
from .models import Ticket, Comentario
from inventario.models import Ubicacion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Submit

# --- Campo de Formulario Personalizado ---
# Para que el menú desplegable de "Banda" muestre solo el nombre de la banda.
class BandaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.banda

class TicketForm(forms.ModelForm):
    """
    Formulario principal para la creación y edición de tickets.

    Este formulario maneja la lógica de negocio completa para un ticket,
    incluyendo campos estándar del modelo, campos para la interfaz de usuario
    (UI) que no se guardan en la base de datos, y una maquetación compleja
    gestionada con Crispy Forms.
    """

    # Constantes de clase
    TACTO_RANGE_START = 1
    TACTO_RANGE_END = 31
    OP_RANGE_START = 10
    OP_RANGE_END = 151
    OP_RANGE_STEP = 10
    MAX_OPERACION_LENGTH = 10

    # --- Campos de UI y Lógica de Búsqueda (no persistentes) ---
    text_search = forms.CharField(
        label="Buscar Herramienta",
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por número de serie o modelo...',
            'hx-post': '/tickets/buscar-herramientas/',
            'hx-trigger': 'keyup changed delay:500ms, search from:closest form',
            'hx-target': '#search-results',
            'hx-indicator': '.htmx-indicator',
            'autocomplete': 'off',
            'id': 'id_text_search'
        })
    )

    # Campos deshabilitados para mostrar información dinámica
    modelo_display = forms.CharField(
        label="Modelo",
        required=False,
        disabled=True
    )
    fabricante_display = forms.CharField(
        label="Fabricante",
        required=False,
        disabled=True
    )
    numero_serie_display = forms.CharField(
        label="Número de Serie",
        required=False,
        disabled=True
    )
    numero_reparacion_display = forms.CharField(
        label="Número de Reparación",
        required=False,
        disabled=True
    )
    fecha_actual = forms.CharField(
        label="Fecha",
        required=False,
        disabled=True
    )
    turno_actual = forms.CharField(
        label="Turno",
        required=False,
        disabled=True
    )
    grupo = forms.CharField(
        label="Grupo Asignado",
        required=False,
        disabled=True,
        initial="Aún no asignado"
    )
    NAVE_CHOICES = [
        ('', '---------'),
        ('A40/41', 'A40/41'),
        ('A50', 'A50'),
        ('A60', 'A60'),
    ]

    nave = forms.ChoiceField(
        label="Nave",
        choices=NAVE_CHOICES,
        required=True
    )

    # --- Campos del Modelo Redefinidos ---
    ubicacion = BandaModelChoiceField(
        label="Banda",
        queryset=Ubicacion.objects.none(),
        required=True,
        widget=forms.Select(attrs={
            'hx-get': '/tickets/get-nave-for-ubicacion/',
            'hx-target': '#nave-container',
            'hx-trigger': 'change',
        })
    )

    tacto = forms.ChoiceField(
        label="Tacto / OP",
        choices=[],  # Se puebla en __init__
        required=False
    )

    operacion = forms.CharField(
        label="Caso de atornillado",
        required=True,
        max_length=MAX_OPERACION_LENGTH,
        widget=forms.TextInput(attrs={
            'placeholder': f'Máx. {MAX_OPERACION_LENGTH} caracteres'
        })
    )

    grupos_notificacion = forms.ModelMultipleChoiceField(
        queryset=GrupoNotificacion.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Notificar a los siguientes grupos",
        required=False
    )
    operacion = forms.CharField(
        label="Caso de atornillado",
        required=True,
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'Máx. 10 caracteres'})
    )

    class Meta:
        """Configuración del Meta para el formulario."""

        model = Ticket
        # Se eliminan los campos 'nombre_reporta', etc.
        fields = ['herramienta', 'ubicacion', 'falla', 'comentarios', 'estado', 'tacto', 'operacion']
        widgets = {
            'herramienta': forms.HiddenInput(),
            'comentarios': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario.

        - Configura el queryset dinámico para el campo 'ubicacion'.
        - Define las opciones del campo 'tacto'.
        - Define la maquetación del formulario utilizando Crispy Forms.
        """
        super().__init__(*args, **kwargs)
        
        # --- Lógica para poblar el campo 'ubicacion' con bandas únicas ---
        unique_band_names = Ubicacion.objects.order_by('banda').values_list('banda', flat=True).distinct()
        pks_of_unique_bands = []
        for band_name in unique_band_names:
            first_ubicacion = Ubicacion.objects.filter(banda=band_name).first()
            if first_ubicacion:
                pks_of_unique_bands.append(first_ubicacion.pk)
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(pk__in=pks_of_unique_bands).order_by('banda')

        # --- Configuración del Layout ---
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            # --- Sección Superior (INTACTA, como la pediste) ---
            Row(
                Column(Field('fecha_actual', readonly=True), css_class='col-md-4'),
                Column(Field('turno_actual', readonly=True), css_class='col-md-4'),
                Column(Field('grupo', readonly=True), css_class='col-md-4')
            ),
            HTML('<hr>'),
            HTML('<h5 class="mb-3">1. Ubicación de la Falla</h5>'),
            Row(
                Column('ubicacion', css_class='col-md-3'),
                Column(
                    HTML('<div id="nave-container">'),
                    'nave_display', 
                    HTML('</div>'),
                    css_class='col-md-3'
                ),
                Column('tacto', css_class='col-md-3'),
                Column('operacion', css_class='col-md-3'),
                css_class='align-items-end'
            ),
            HTML('<hr>'),

            # --- SECCIÓN DE HERRAMIENTA (AÑADIDA COMO LA QUERÍAS) ---
            HTML('<h5 class="mb-3">2. Datos de la Herramienta</h5>'),
            'text_search',
            HTML('<div class="htmx-indicator text-muted small">Buscando...</div>'),
            Row(
                Column(Field('modelo_display', readonly=True)),
                Column(Field('fabricante_display', readonly=True)),
            ),
            Row(
                Column(Field('numero_serie_display', readonly=True)),
                Column(Field('numero_reparacion_display', readonly=True)),
            ),
            HTML('<div id="search-results" class="list-group mb-3"></div>'),
            'herramienta', # Campo oculto
            HTML('<div id="ticket-duplicado-warning" class="mt-2"></div>'),
            HTML('<hr>'),

            # --- SECCIONES FINALES (AJUSTADAS Y SIN CAMPOS EXTRA) ---
            HTML('<h5 class="mb-3">3. Descripción de la Falla</h5>'),
            Row(Column('falla'), Column('comentarios')),
            HTML('<hr>'),
            HTML('<h5 class="mb-3">4. Estado del Ticket</h5>'),
            'estado',
            
            Submit('submit', 'Guardar Ticket', css_class='btn btn-primary mt-4 w-100')
        )



# --- Formularios Adicionales (Sin Cambios) ---
class ActualizarEstadoForm(forms.ModelForm):
    """Formulario simple para actualizar únicamente el estado de un ticket."""

    class Meta:
        """Configuración del Meta para el formulario."""

        model = Ticket
        fields = ['estado']
        labels = { 'estado': '' }

class ComentarioForm(forms.ModelForm):
    """Formulario para la creación de nuevos comentarios en un ticket."""

    class Meta:
        """Configuración del Meta para el formulario."""

        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Añade una actualización o nota...'
            }),
        }
        labels = { 'texto': 'Nuevo Comentario' }