#!/bin/sh
# Entrypoint script para Docker

set -e

echo "Esperando a que PostgreSQL esté listo..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "postgres" -c '\q' 2>/dev/null; do
  >&2 echo "PostgreSQL no está disponible - esperando..."
  sleep 1
done

echo "PostgreSQL está listo - continuando..."

# Aplicar migraciones
echo "Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe (solo en desarrollo)
if [ "$DEBUG" = "True" ]; then
    echo "Modo desarrollo detectado"
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
END
fi

echo "Iniciando servidor..."
exec "$@"
