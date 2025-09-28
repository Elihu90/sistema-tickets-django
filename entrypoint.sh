
#!/bin/sh
set -e  # Detener si hay error

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput

echo "Ejecutando scripts de importación..."

# Ejecuta tus comandos de Django
python manage.py import_herramientas
python manage.py import_colaboradores
python manage.py poblar_ubicaciones
python manage.py generar_tickets_falsos

echo "Todos los scripts ejecutados correctamente."

# Inicia Gunicorn
exec "$@"
