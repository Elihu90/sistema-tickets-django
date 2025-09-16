

# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Colaborador, GrupoNotificacion

# Define un "inline" para el modelo Colaborador
class ColaboradorInline(admin.StackedInline):
    model = Colaborador
    can_delete = False
    verbose_name_plural = 'perfil de colaborador'

# Define una nueva clase de admin para User
class UserAdmin(BaseUserAdmin):
    inlines = [ColaboradorInline]

# Re-registra el modelo User con el nuevo UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(GrupoNotificacion)