# tickets/forms.py

from django import forms
from .models import Ticket, Herramienta
from usuarios.models import GrupoNotificacion

# Crispy Forms
from crispy_forms.helper import FormHelper
# ¡Añadimos HTML a la importación!
from crispy_forms.layout import Layout, Row, Column, Field, HTML

class TicketForm(forms.ModelForm):
    text_search = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Busca la herramienta por número de serie o modelo...',
            'hx-post': '/tickets/buscar-herramientas/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#search-results',
            'hx-indicator': '.htmx-indicator',
        })
    )
    
    grupos_notificacion = forms.ModelMultipleChoiceField(
        queryset=GrupoNotificacion.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Notificar a los siguientes grupos",
        required=False
    )

    class Meta:
        model = Ticket
        fields = [
            'herramienta', 'falla', 'ubicacion', 'comentarios', 'numero_ticket_externo',
        ]
        widgets = {
            'herramienta': forms.HiddenInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'text_search',
            
            # --- CORRECCIÓN AQUÍ ---
            # Envolvemos el HTML en el objeto HTML()
            HTML('<div class="htmx-indicator">Buscando...</div>'),
            HTML('<div id="search-results" class="list-group mb-3"></div>'),
            HTML('<div id="herramienta-details"></div>'),
            
            'herramienta', 
            
            Row(
                Column('falla', css_class='form-group col-md-6 mb-0'),
                Column('ubicacion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'comentarios',
            'numero_ticket_externo',
            'grupos_notificacion'
        )