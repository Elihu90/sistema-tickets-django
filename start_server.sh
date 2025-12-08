#!/bin/bash
# ========================================
# Sistema de Tickets - Inicio en Red Local
# ========================================

echo "========================================"
echo "Sistema de Tickets - Inicio"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "ERROR: No se encontró el entorno virtual"
    echo ""
    echo "Creando entorno virtual..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo crear el entorno virtual"
        exit 1
    fi
    echo "Entorno virtual creado exitosamente"
fi

# Activar entorno virtual
source .venv/bin/activate

# Verificar si requirements.txt existe e instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "Verificando dependencias..."
    pip install -q -r requirements.txt
fi

# Configurar variables de entorno para desarrollo local
export DEBUG=True
export ALLOWED_HOSTS="*"

# Obtener IP local
IP=$(hostname -I | awk '{print $1}')

# Crear directorio de logs si no existe
mkdir -p logs

echo ""
echo "Aplicando migraciones..."
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Hubo un problema al aplicar las migraciones"
    echo "Revisa los errores anteriores"
    exit 1
fi

echo ""
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo ""
echo "========================================"
echo "Servidor Iniciado Exitosamente"
echo "========================================"
echo ""
echo "Acceso local:  http://localhost:8000"
echo "Acceso en red: http://$IP:8000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "========================================"
echo ""

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
