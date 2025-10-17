# tickets/forms.py

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
    Formulario unificado para la creación de tickets.
    """
    # --- Campos que NO están en el modelo (usados para la UI) ---
    fecha_actual = forms.CharField(label="Fecha", required=False, disabled=True)
    turno_actual = forms.CharField(label="Turno", required=False, disabled=True)
    grupo = forms.CharField(label="Grupo Asignado", required=False, disabled=True, initial="Aún no asignado")
    
    # Campos para la búsqueda y visualización de la herramienta
    text_search = forms.CharField(
        label="Buscar Herramienta (por modelo, serie o # reparación)",
        required=True,
        widget=forms.TextInput(attrs={
            'hx-post': '/tickets/buscar-herramienta/', # Asegúrate que la URL sea la correcta
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#search-results',
            'autocomplete': 'off',
            'placeholder': 'Escribe para buscar...'
        })
    )
    modelo_display = forms.CharField(label="Modelo", required=False, disabled=True)
    fabricante_display = forms.CharField(label="Fabricante", required=False, disabled=True)
    numero_serie_display = forms.CharField(label="Número de Serie", required=False, disabled=True)
    numero_reparacion_display = forms.CharField(label="# Reparación", required=False, disabled=True)

    # --- Campos del modelo redefinidos para la nueva lógica de ubicación ---
    ubicacion = BandaModelChoiceField(
        label="Banda",
        queryset=Ubicacion.objects.none(), # Se llenará en __init__
        required=True,
        widget=forms.Select(attrs={
            'hx-get': '/tickets/get-nave-for-ubicacion/', # Asegúrate que la URL sea la correcta
            'hx-target': '#nave-container',
            'hx-trigger': 'change',
        })
    )
    nave_display = forms.CharField(label="Nave", required=False, disabled=True)
    TACTO_CHOICES = [('', '---------')] + \
                      [(str(i), str(i)) for i in range(1, 31)] + \
                      [(f'OP{j}', f'OP{j}') for j in range(10, 151, 10)]
    tacto = forms.ChoiceField(
        label="Tacto / OP",
        choices=TACTO_CHOICES,
        required=False
    )
    operacion = forms.CharField(
        label="Caso de atornillado",
        required=True,
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'Máx. 10 caracteres'})
    )

    class Meta:
        model = Ticket
        # Se eliminan los campos 'nombre_reporta', etc.
        fields = ['herramienta', 'ubicacion', 'falla', 'comentarios', 'estado', 'tacto', 'operacion']
        widgets = {
            'herramienta': forms.HiddenInput(),
            'comentarios': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
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
    class Meta:
        model = Ticket
        fields = ['estado']
        labels = { 'estado': '' }

class ComentarioForm(forms.ModelForm):
    class Meta:
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