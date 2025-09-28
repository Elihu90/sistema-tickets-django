# tickets/forms.py

from django import forms
from .models import Ticket, Comentario # He añadido Comentario aquí por el otro formulario
from usuarios.models import GrupoNotificacion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Submit

# --- Opciones para campos Choice ---
TACTO_CHOICES = [('', 'Seleccionar Tacto')] + [(str(i), str(i)) for i in range(1, 31)]
OPERACION_CHOICES = [('', 'Seleccionar Operación')] + [(f'OP {i*10}', f'OP {i*10}') for i in range(1, 16)]

# ==============================================================================
# FORMULARIO PRINCIPAL PARA CREAR Y EDITAR TICKETS
# ==============================================================================
class TicketForm(forms.ModelForm):
    # --- Tus campos que no están en el modelo (SIN CAMBIOS) ---
    text_search = forms.CharField(label="Buscar Herramienta", required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Buscar por número de serie o modelo...',
        'hx-post': '/tickets/buscar-herramientas/',
        'hx-trigger': 'keyup changed delay:500ms', 'hx-target': '#search-results',
        'hx-indicator': '.htmx-indicator',
    }))
    
    modelo_display = forms.CharField(label="Modelo", required=False, disabled=True)
    fabricante_display = forms.CharField(label="Fabricante", required=False, disabled=True)
    numero_serie_display = forms.CharField(label="Número de Serie", required=False, disabled=True)
    numero_reparacion_display = forms.CharField(label="Número de Reparación", required=False, disabled=True)
    nombre_reporta = forms.CharField(label="Quien Reporta", required=False, disabled=True)
    puesto_reporta = forms.CharField(label="Puesto", required=False, disabled=True)
    email_reporta = forms.EmailField(label="Correo Electrónico", required=False, disabled=True)
    nave_display = forms.CharField(label="Nave", required=False, disabled=True)
    fecha_actual = forms.CharField(label="Fecha", required=False, disabled=True)
    turno_actual = forms.CharField(label="Turno", required=False, disabled=True)

    # --- Tus campos del modelo con widgets personalizados (SIN CAMBIOS) ---
    tacto = forms.ChoiceField(choices=TACTO_CHOICES, required=False)
    operacion = forms.ChoiceField(choices=OPERACION_CHOICES, required=False)
    grupos_notificacion = forms.ModelMultipleChoiceField(
        queryset=GrupoNotificacion.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Notificar a los siguientes grupos",
        required=False
    )
    
    class Meta:
        model = Ticket
        # ⭐ 1. AÑADIMOS 'estado' A LA LISTA DE CAMPOS MANEJADOS POR EL FORMULARIO ⭐
        fields = ['herramienta', 'falla', 'ubicacion', 'comentarios', 'tacto', 'operacion', 'estado']
        widgets = {
            'herramienta': forms.HiddenInput(),
            'comentarios': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            # --- Tu layout (SIN CAMBIOS) ---
            Row(Field('fecha_actual', readonly=True), Field('turno_actual', readonly=True)),
            HTML('<hr>'),
            HTML('<h5 class="mb-3">1. Datos de Quien Reporta</h5>'),
            Row(Column('nombre_reporta'), Column('puesto_reporta'), Column('email_reporta')),
            HTML('<hr>'),
            HTML('<h5 class="mb-3">2. Ubicación de la Falla</h5>'),
            Row(Column('ubicacion'), Column('nave_display'), Column('tacto'), Column('operacion')),
            HTML('<hr>'),
            HTML('<h5 class="mb-3">3. Datos de la Herramienta</h5>'),
            'text_search',
            HTML('<div class="htmx-indicator">Buscando...</div>'),
            Row(Column('modelo_display'), Column('fabricante_display')),
            Row(Column('numero_serie_display'), Column('numero_reparacion_display')),
            HTML('<div id="search-results" class="list-group mb-3"></div>'),
            'herramienta',
            HTML('<div id="ticket-duplicado-warning"></div>'),
            HTML('<hr>'),
            HTML('<h5 class="mb-3">4. Descripción de la Falla y Notificación</h5>'),
            Row(Column('falla'), Column('comentarios')),
            HTML('<div class="card mt-3"><div class="card-body">'),
            'grupos_notificacion',
            HTML('</div></div>'),
            
            # ⭐ 2. AÑADIMOS EL CAMPO 'estado' A LA ESTRUCTURA VISUAL DEL FORMULARIO ⭐
            HTML('<hr>'),
            HTML('<h5 class="mb-3">5. Estado del Ticket</h5>'),
            'estado',
            
            Submit('submit', 'Guardar Ticket', css_class='btn btn-primary mt-4 w-100')
        )

# ==============================================================================
# TU FORMULARIO PARA ACTUALIZAR ESTADO (SIN CAMBIOS)
# ==============================================================================
class ActualizarEstadoForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['estado']
        labels = {
            'estado': '',
        }
        
# ==============================================================================
# TU FORMULARIO DE COMENTARIOS (SIN CAMBIOS)
# ==============================================================================
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
        labels = {
            'texto': 'Nuevo Comentario'
        }