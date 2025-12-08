#!/bin/bash

# Script de Despliegue Universal para SGTR (Linux)
# Soporta modos Docker y Nativo

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

log() {
    echo -e "${2}${1}${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log "Por favor ejecuta este script como root (sudo)." "$RED"
        exit 1
    fi
}

setup_native() {
    log "\n=== Configuración Nativa (Portable) ===" "$CYAN"

    # 1. Verificar Python
    if ! command -v python3 &> /dev/null; then
        log "Python 3 no encontrado. Intentando instalar..." "$YELLOW"
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y python3 python3-venv python3-pip
        elif command -v yum &> /dev/null; then
            yum install -y python3
        else
            log "No se pudo instalar Python automáticamente. Instálalo manualmente." "$RED"
            exit 1
        fi
    fi

    # 2. Entorno Virtual
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        log "Creando entorno virtual..." "$YELLOW"
        python3 -m venv "$SCRIPT_DIR/.venv"
    fi

    # 3. Dependencias
    log "Instalando dependencias..." "$YELLOW"
    "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    "$SCRIPT_DIR/.venv/bin/pip" install waitress gunicorn

    # 4. Configuración .env
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        log "Creando archivo .env..." "$YELLOW"
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        # Generar secret key simple
        sed -i "s/django-insecure-change-this-in-production/$(date +%s | sha256sum | base64 | head -c 32)/" "$SCRIPT_DIR/.env"
        # Forzar SQLite
        sed -i 's/^DATABASE_URL=/# DATABASE_URL=/' "$SCRIPT_DIR/.env"
    fi

    # 5. Base de Datos y Estáticos
    log "Ejecutando migraciones..." "$YELLOW"
    "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/manage.py" migrate
    
    log "Recolectando estáticos..." "$YELLOW"
    "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/manage.py" collectstatic --noinput

    # 6. Ejecutar
    log "\n=== Instalación Completada ===" "$GREEN"
    IP=$(hostname -I | cut -d' ' -f1)
    log "Iniciando servidor en http://$IP:8000" "$CYAN"
    
    # Usar Gunicorn en Linux en lugar de Waitress
    "$SCRIPT_DIR/.venv/bin/gunicorn" sgtr.wsgi:application --bind 0.0.0.0:8000 --workers 3
}

setup_docker() {
    log "\n=== Configuración Docker ===" "$CYAN"
    
    if ! command -v docker &> /dev/null; then
        log "Docker no encontrado. Por favor instálalo primero." "$RED"
        exit 1
    fi

    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    fi

    log "Iniciando contenedores..." "$YELLOW"
    docker-compose up -d --build

    log "Esperando DB..." "$YELLOW"
    sleep 10

    log "Migrando..." "$YELLOW"
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py collectstatic --noinput

    log "\n=== Despliegue Docker Completado ===" "$GREEN"
}

# Main
clear
log "=== SGTR: Sistema de Gestión de Tickets ===" "$CYAN"
log "1. NATIVO (Portable)" "$GREEN"
log "2. DOCKER" "$CYAN"
read -p "Opción: " option

case $option in
    1) setup_native ;;
    2) setup_docker ;;
    *) log "Opción inválida" "$RED" ;;
esac
