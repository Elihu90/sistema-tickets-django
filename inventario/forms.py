from django import forms
from django.contrib.auth.models import User
from usuarios.models import Colaborador

class ColaboradorForm(forms.ModelForm):
    # Campos para el modelo User
    username = forms.CharField(label="Usuario", max_length=150, required=True)
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Correo Electrónico", required=True)
    
    class Meta:
        model = Colaborador
        fields = ['puesto', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si estamos editando, poblamos los campos del usuario
            self.fields['username'].initial = self.instance.usuario.username
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email
            # El username no debería cambiarse fácilmente para no romper logins, 
            # pero lo dejaremos editable por ahora o readonly si se prefiere.
            # self.fields['username'].disabled = True 

    def save(self, commit=True):
        # 1. Guardar/Crear Usuario
        if self.instance.pk:
            user = self.instance.usuario
        else:
            user = User()
            # Contraseña por defecto o generada. Aquí usaremos el username como pass temporal
            # Ojo: En producción esto debería manejarse mejor (email de invitación).
            user.set_password('temporal123') 

        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()

        # 2. Guardar Colaborador
        colaborador = super().save(commit=False)
        colaborador.usuario = user
        
        if commit:
            colaborador.save()
            
        return colaborador
