# Script de diagnóstico para verificar configuración de email
# Ejecutar en el servidor Lightsail

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Cargar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgtr.settings')
import django
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("DIAGNÓSTICO DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)

print("\n1. Variables de entorno:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

if not settings.DEBUG:
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADO'}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
else:
    print("   ⚠️  DEBUG está en True - los emails irán a la consola")

print("\n2. Probando envío de email de prueba...")
try:
    send_mail(
        'Test desde SGTR',
        'Este es un email de prueba para verificar la configuración.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER],  # Enviar a ti mismo
        fail_silently=False,
    )
    print("   ✅ Email enviado exitosamente!")
    print("   Revisa tu bandeja de entrada.")
except Exception as e:
    print(f"   ❌ ERROR al enviar email:")
    print(f"   {type(e).__name__}: {str(e)}")
    
print("\n" + "=" * 60)
