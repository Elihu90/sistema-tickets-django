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

from usuarios.models import GrupoNotificacion

from .models import Comentario, Ticket, Ubicacion


# ==============================================================================
# CAMPOS DE FORMULARIO PERSONALIZADOS
# ==============================================================================

class BandaModelChoiceField(forms.ModelChoiceField):
    """
    Campo de formulario personalizado para mostrar solo el nombre de la banda.

    Sobrescribe el método `label_from_instance` para que el menú desplegable
    de 'ubicacion' muestre un valor legible por el usuario (el nombre de la
    banda) en lugar de la representación de objeto predeterminada de Django.
    """

    def label_from_instance(self, obj):
        """Devuelve el nombre de la banda para la instancia de Ubicacion."""
        return f"{obj.banda}"


# ==============================================================================
# FORMULARIOS PRINCIPALES DE LA APLICACIÓN
# ==============================================================================

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

    class Meta:
        """Configuración del Meta para el formulario."""

        model = Ticket
        fields = [
            'herramienta',
            'falla',
            'ubicacion',
            'nave',
            'comentarios',
            'tacto',
            'operacion',
            'estado'
        ]
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

        # Configurar opciones de tacto dinámicamente
        self._setup_tacto_choices()

        # Configurar queryset de ubicacion
        self._setup_ubicacion_queryset()

        # Configurar layout de Crispy Forms
        self._setup_crispy_layout()

    def _setup_tacto_choices(self):
        """Configura las opciones del campo tacto."""
        tacto_choices = [('', '---------')]

        # Agregar números del 1 al 30
        tacto_choices.extend([
            (str(i), str(i))
            for i in range(self.TACTO_RANGE_START, self.TACTO_RANGE_END)
        ])

        # Agregar opciones OP (10, 20, ..., 150)
        tacto_choices.extend([
            (f'OP{j}', f'OP{j}')
            for j in range(
                self.OP_RANGE_START,
                self.OP_RANGE_END,
                self.OP_RANGE_STEP
            )
        ])

        self.fields['tacto'].choices = tacto_choices

    def _setup_ubicacion_queryset(self):
        """Configura el queryset de ubicacion con bandas únicas."""
        unique_band_names = Ubicacion.objects.order_by('banda').values_list(
            'banda', flat=True
        ).distinct()

        pks_of_unique_bands = [
            Ubicacion.objects.filter(banda=name).first().pk
            for name in unique_band_names
            if Ubicacion.objects.filter(banda=name).exists()
        ]

        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(
            pk__in=pks_of_unique_bands
        ).order_by('banda')

    def _setup_crispy_layout(self):
        """Configura el layout del formulario con Crispy Forms."""
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            # Información general (no editable)
            Row(
                Column(
                    Field('fecha_actual', readonly=True),
                    css_class='col-md-4'
                ),
                Column(
                    Field('turno_actual', readonly=True),
                    css_class='col-md-4'
                ),
                Column(
                    Field('grupo', readonly=True),
                    css_class='col-md-4'
                )
            ),
            HTML('<hr>'),

            # Sección 1: Ubicación de la falla
            HTML('<h5 class="mb-3">1. Ubicación de la Falla</h5>'),
            Row(
                Column('ubicacion', css_class='col-md-3'),
                Column('nave', css_class='col-md-3'),
                Column('tacto', css_class='col-md-3'),
                Column('operacion', css_class='col-md-3'),
                css_class='align-items-end'
            ),
            HTML('<hr>'),

            # Sección 2: Datos de la herramienta
            HTML('<h5 class="mb-3">2. Datos de la Herramienta</h5>'),
            HTML('''
                <div class="search-container mb-3">
                    <input type="hidden" id="primera-busqueda" value="true">
                </div>
            '''),
            'text_search',
            HTML('<div class="htmx-indicator">Buscando...</div>'),
            HTML('''
                <div id="search-results" class="list-group mb-3"></div>
                <div id="no-results-alert" class="alert alert-warning" 
                     style="display:none;">
                    <h5>⚠️ Herramienta no encontrada</h5>
                    <p>No se encontró ninguna herramienta con ese criterio.</p>
                    <button type="button" class="btn btn-primary" 
                            onclick="mostrarModalCrearHerramienta()">
                        ➕ Crear Nueva Herramienta
                    </button>
                </div>
            '''),
            Row(
                Column('modelo_display'),
                Column('fabricante_display')
            ),
            Row(
                Column('numero_serie_display'),
                Column('numero_reparacion_display')
            ),
            'herramienta',
            HTML('<div id="ticket-duplicado-warning"></div>'),
            HTML('<hr>'),

            # Sección 3: Descripción y notificaciones
            HTML('<h5 class="mb-3">3. Descripción de la Falla y '
                 'Notificación</h5>'),
            Row(
                Column('falla'),
                Column('comentarios')
            ),
            HTML('<div class="card mt-3"><div class="card-body">'),
            'grupos_notificacion',
            HTML('</div></div>'),
            HTML('<hr>'),

            # Sección 4: Estado del ticket
            HTML('<h5 class="mb-3">4. Estado del Ticket</h5>'),
            'estado',

            # Botón de envío
            Submit(
                'submit',
                'Guardar Ticket',
                css_class='btn btn-primary mt-4 w-100'
            )
        )


class ActualizarEstadoForm(forms.ModelForm):
    """Formulario simple para actualizar únicamente el estado de un ticket."""

    class Meta:
        """Configuración del Meta para el formulario."""

        model = Ticket
        fields = ['estado']
        labels = {
            'estado': ''
        }


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
        labels = {
            'texto': 'Nuevo Comentario'
        }