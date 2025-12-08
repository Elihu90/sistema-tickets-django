# Script para diagnosticar por qué el servidor no responde
# Ejecutar en el servidor Lightsail

import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgtr.settings')

print("=" * 60)
print("DIAGNÓSTICO DE SERVIDOR")
print("=" * 60)

# 1. Verificar que Django puede importarse
try:
    import django
    django.setup()
    print("✅ Django se importó correctamente")
except Exception as e:
    print(f"❌ Error al importar Django: {e}")
    sys.exit(1)

# 2. Verificar configuración
from django.conf import settings
print(f"\n✅ DEBUG: {settings.DEBUG}")
print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"✅ DATABASE: {settings.DATABASES['default']['ENGINE']}")

# 3. Verificar base de datos
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Conexión a base de datos OK")
except Exception as e:
    print(f"❌ Error de base de datos: {e}")

# 4. Verificar que las URLs funcionan
try:
    from django.urls import reverse
    home_url = reverse('home')
    print(f"✅ URL 'home' resuelve a: {home_url}")
except Exception as e:
    print(f"❌ Error en URLs: {e}")

# 5. Probar una vista simple
try:
    from django.test import Client
    client = Client()
    print("\n🔍 Probando petición GET a '/'...")
    response = client.get('/')
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ La vista responde correctamente")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Contenido: {response.content[:200]}")
except Exception as e:
    print(f"   ❌ Error al probar vista: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
